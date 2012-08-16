
from urllib2 import unquote
from urlparse import urlsplit

from zope.interface import implements, Interface
from plone.transformchain.interfaces import ITransform
from plone.app.theming.interfaces import IThemingLayer
from zope.component import adapts

import newrelic.agent

class NewRelic(object):
    """Outputfilter that adds NewRelic Real User Monitoring to content"""
    implements(ITransform)
    adapts(Interface, IThemingLayer)

    order = 9000  # Late, after Diazo does it's job

    blacklist_extensions = ('html', 'xhtml', 'com')

    asset_views = ('view', 'download')

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request

    def _transform(self, data):
        """ check if we should transform, or return unchanged data """

        request = self.request
        response = request.response

        parents = self.request.get('PARENTS', None)
        if not parents:
            return data
        context = parents[0]

        # Check request type
        content_type = response.getHeader('content-type')
        if not content_type or \
            not (content_type.startswith('text/html') or
                    content_type.startswith('application/xhtml+xml')):
            return data

        return data
        return self._apply_transform(context, data)

    def _apply_transform(self, context, data):
        """Apply the filter.
        ``data`` is a UTF-8-encoded string.
        Return a UTF-8-encoded string, or ``None`` to indicate that the data
        should remain unmodified.
        """

        trans = newrelic.agent.current_transaction()

        if False and  trans is not None:
            data = data.replace('<head>' , "<head>\n%s" % trans.browser_timing_header() )
            data = data.replace('</html>', "%s\n</html>" % trans.browser_timing_footer() )
            print 'Wel RUM'

        return data

    def transformString(self, result, encoding):
        return self._transform(result)

    def transformUnicode(self, result, encoding):
        return self._transform(result)

    def transformIterable(self, result, encoding):
        return [self._transform(s) for s in result]


