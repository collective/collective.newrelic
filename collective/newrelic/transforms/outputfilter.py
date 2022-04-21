from zope.interface import implementer, Interface
from plone.transformchain.interfaces import ITransform

# Try to use plone.app.theming. If that fails use zope.interface.Interface
# zope.interface.Interface results that every requests is adapted instead of a theming layer.
try:
    from plone.app.theming.interfaces import IThemingLayer
except ImportError:
    from zope.interface import Interface as IThemingLayer

from zope.component import adapter

import newrelic.agent

from lxml import etree
from lxml.html import fragment_fromstring
from repoze.xmliter.utils import getHTMLSerializer
from collective.newrelic.utils import PLACEHOLDER


@implementer(ITransform)
@adapter(Interface, IThemingLayer)
class NewRelic(object):
    """Outputfilter that adds NewRelic Real User Monitoring to content.

    Late stage in the 8000's transform chain. When plone.app.blocks is
    used, we can benefit from lxml parsing having taken place already.
    """

    order = 8860  # Later than Diazo (8850)

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request

    def parseTree(self, result):
        contentType = self.request.response.getHeader('Content-Type')
        if contentType is None or not contentType.startswith('text/html'):
            return None

        contentEncoding = self.request.response.getHeader('Content-Encoding')
        if contentEncoding and contentEncoding in ('zip', 'deflate', 'compress',):
            return None

        try:
            return getHTMLSerializer(result, pretty_print=False)
        except (AttributeError, TypeError, etree.ParseError):
            return None

    def transformString(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformUnicode(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformIterable(self, result, encoding):
        settings = newrelic.agent.global_settings()
        if not settings.browser_monitoring.auto_instrument:
            return result

        result = self.parseTree(result)
        if result is None:
            return None

        trans = newrelic.agent.current_transaction()

        if trans is None:
            return result

        if trans.name == PLACEHOLDER:
            return result

        head = result.tree.find('head')
        foot = result.tree.find('body')
        if head is not None and len(head) and foot is not None and len(foot):
            nr_header = trans.browser_timing_header()
            nr_footer = trans.browser_timing_footer()
            if nr_header and nr_footer:
                o_head = fragment_fromstring(nr_header)
                # Use a comment wrapper to avoid XML entity conversion
                head_script = etree.Comment('\n' + o_head.text + '\n//')
                o_head.text = '//'
                o_head.append(head_script)
                head.insert(0, o_head)  # Before the first child of head

                o_foot = fragment_fromstring(nr_footer)
                foot_script = etree.Comment('\n' + o_foot.text + '\n//')
                o_foot.text = '//'
                o_foot.append(foot_script)
                foot.insert(len(foot.getchildren()),
                            o_foot)  # After the last child of body

        return result
