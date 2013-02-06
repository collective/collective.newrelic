import newrelic.agent
import newrelic.api

from Products.CMFPlone.CatalogTool import CatalogTool

CatalogTool.original_cmfplone_catalogtool_searchResults = CatalogTool.searchResults

def newrelic_searchResults(self, REQUEST=None, **kw):
    trans = newrelic.agent.current_transaction()

    with newrelic.api.database_trace.DatabaseTrace(trans, str(kw), self):
        result = self.original_cmfplone_catalogtool_searchResults(REQUEST, **kw)

    return result

CatalogTool.searchResults = newrelic_searchResults


