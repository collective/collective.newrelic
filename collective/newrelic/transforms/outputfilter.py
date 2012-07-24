from Products.CMFCore.utils import getToolByName
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from urllib2 import unquote
from urlparse import urlsplit

import newrelic.agent

class NewRelic(object):
    """Outputfilter that adds sizes to links to images / files"""

    order = 666  # early, before Diazo does it's job

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

        return self._apply_transform(context, data)

    def _apply_transform(self, context, data):
        """Apply the filter.
        ``data`` is a UTF-8-encoded string.
        Return a UTF-8-encoded string, or ``None`` to indicate that the data
        should remain unmodified.
        """

        try:
            utool = getToolByName(context, 'portal_url')
            ctool = getToolByName(context, 'portal_catalog')
            mimereg = getToolByName(context, 'mimetypes_registry')
        except:
            return data

        soup = BeautifulSoup(data)
        body = soup.find('body')
        head = soup.find('head')

        trans = newrelic.agent.current_transaction()

        head.insert( 99 , NavigableString( trans.browser_timing_header() ) )
        body.insert( 99 , NavigableString( trans.browser_timing_footer() ) )      

        return str(soup)

    def transformString(self, result, encoding):
        return self._transform(result)

    def transformUnicode(self, result, encoding):
        return self._transform(result)

    def transformIterable(self, result, encoding):
        return [self._transform(s) for s in result]
