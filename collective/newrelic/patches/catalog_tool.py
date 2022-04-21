import newrelic.agent
import newrelic.api

from Products.CMFPlone.CatalogTool import CatalogTool
from collective.newrelic.utils import logger

CatalogTool.original_cmfplone_catalogtool_searchResults = CatalogTool.searchResults
newrelic.api.database_trace.register_database_client(CatalogTool, 'Plone Catalog')


def newrelic_searchResults(self, REQUEST=None, **kw):
    if isinstance(REQUEST, dict):
        dump = str(REQUEST)
    else:
        dump = str(kw)
    request_environ = getattr(self, 'REQUEST', {}).get('environ', {})
    host = request_environ.get('REMOTE_HOST', None)
    port = str(request_environ.get('SERVER_PORT', '')) or None
    db_name = self.getId()
    with newrelic.api.database_trace.DatabaseTrace(
            dump, dbapi2_module=CatalogTool, host=host,
            port_path_or_id=port, database_name=db_name):
        result = self.original_cmfplone_catalogtool_searchResults(
            REQUEST, **kw
        )

    return result


CatalogTool.searchResults = newrelic_searchResults
logger.info("Patched Products.CMFPlone.CatalogTool:CatalogTool.searchResults with instrumentation")
