import newrelic.agent
import newrelic.api

from Products.CMFPlone.CatalogTool import CatalogTool
from collective.newrelic.utils import logger

CatalogTool.original_cmfplone_catalogtool_searchResults = CatalogTool.searchResults


def newrelic_searchResults(self, REQUEST=None, **kw):
    trans = newrelic.agent.current_transaction()

    if isinstance(REQUEST, dict):
    	dump = str(REQUEST)
    else:
    	dump = str(kw)
    with newrelic.api.database_trace.DatabaseTrace(trans, dump, self):
        result = self.original_cmfplone_catalogtool_searchResults(REQUEST, **kw)

    return result

CatalogTool.searchResults = newrelic_searchResults
logger.info("Patched Products.CMFPlone.CatalogTool:CatalogTool.searchResults with instrumentation")
