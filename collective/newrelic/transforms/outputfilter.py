from zope.interface import implements, Interface
from plone.transformchain.interfaces import ITransform
from plone.app.theming.interfaces import IThemingLayer
from zope.component import adapts

import newrelic.agent

from lxml import etree
from repoze.xmliter.utils import getHTMLSerializer

class NewRelic(object):
    """Outputfilter that adds NewRelic Real User Monitoring to content.

    Late stage in the 8000's transform chain. When plone.app.blocks is
    used, we can benefit from lxml parsing having taken place already.
    """
    implements(ITransform)
    adapts(Interface, IThemingLayer)

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
        except (TypeError, etree.ParseError):
            return None

    def transformString(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformUnicode(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformIterable(self, result, encoding):
        result = self.parseTree(result)
        if result is None:
            return None

        trans = newrelic.agent.current_transaction()

        if trans is None:
            return result

        head = result.tree.find('head')
        if len(head):
            o = etree.XML(trans.browser_timing_header())
            head.insert( 0, o )  # Before the first child of head

        foot = result.tree.find('body')
        if len(foot):
            o = etree.XML(trans.browser_timing_footer())
            foot.insert( len(foot.getchildren()), o )  # After the last child of body

        return result

