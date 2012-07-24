__import__('pkg_resources').declare_namespace(__name__)

import newrelic.agent
import newrelic.api.transaction
import newrelic.api.web_transaction

from ZPublisher.mapply import (mapply, default_missing_name, default_handle_class)
from ZPublisher.Publish import (call_object, missing_name, dont_publish_class,
                                get_module_info, Retry, publish)

original_publish = publish
original_mapply = mapply

import ZPublisher.Publish

def newrelic_mapply(object, positional=(), keyword={},
           debug=None, maybe=None,
           missing_name=default_missing_name,
           handle_class=default_handle_class,
           context=None, bind=0,
           ):

    trans = newrelic.agent.current_transaction()
    with newrelic.api.function_trace.FunctionTrace(trans,
                                                   name=object.__class__.__name__, 
                                                   group='Zope'):
        result = orginal_mapply(object, positional, keyword, debug, maybe, missing_name, handle_class, context, bind)

    return result

ZPublisher.Publish.mapply = newrelic_mapply

def newrelic_publish(request, module_name, after_list, debug=0,
            # Optimize:
            call_object=call_object,
            missing_name=missing_name,
            dont_publish_class=dont_publish_class,
            mapply=mapply,
            ):

    application = newrelic.api.application.application()
    environ = {}

    trans = newrelic.api.web_transaction.WebTransaction(application,environ)

    trans.name_transaction(request['PATH_INFO'][1:], priority=1)
    trans.__enter__()

    result = original_publish(request, module_name, after_list, debug, call_object, missing_name, dont_publish_class, mapply)
    
    trans.__exit__(None, None, None)

    return result

ZPublisher.Publish.publish = newrelic_publish

from plone.transformchain.transformer import *

original_transform_call = Transformer.__call__

def newrelic_transform__call__(self, request, result, encoding):

    # Don't transform FTP requests
    if isinstance(request, FTPRequest):
        return None

    # Off switch
    if request.environ.get(DISABLE_TRANSFORM_REQUEST_KEY, False):
        return None

    try:
        published = request.get('PUBLISHED', None)

        handlers = [v[1] for v in getAdapters((published, request,), ITransform)]
        handlers.sort(sort_key)

        trans = newrelic.agent.current_transaction()

        for handler in handlers:
            with newrelic.agent.FunctionTrace(trans, handler.__class__.__name__, 'Zope/Transform'):

                if isinstance(result, unicode):
                    newResult = handler.transformUnicode(result, encoding)
                elif isinstance(result, str):
                    newResult = handler.transformBytes(result, encoding)
                else:
                    newResult = handler.transformIterable(result, encoding)

                if newResult is not None:
                    result = newResult

        return result
    except ConflictError:
        raise
    except Exception, e:
        LOGGER.exception(u"Unexpected error whilst trying to apply transform chain")

Transformer.__call__ = newrelic_transform__call__

from zope.event import *

def newrelic_notify(event):
    """ Notify all subscribers of ``event``.
    """
    for subscriber in subscribers:
        nr_relic_subscriber = newrelic.agent.FunctionTraceWrapper(subscriber, event.__class__.__name__, 'Zope/Dispatch')
        nr_relic_subscriber(event)

notify = newrelic_notify

from Products.CMFPlone.CatalogTool import CatalogTool

CatalogTool.original_cmfplone_catalogtool_searchResults = CatalogTool.searchResults

def newrelic_searchResults(self, REQUEST=None, **kw):
    trans = newrelic.agent.current_transaction()

#    with newrelic.api.function_trace.FunctionTrace(trans,
#                                                   name=str(kw), 
#                                                   group='CatalogTool'):        
    with newrelic.api.database_trace.DatabaseTrace(trans, str(kw), self):
        result = self.original_cmfplone_catalogtool_searchResults(REQUEST, **kw)

    return result

CatalogTool.searchResults = newrelic_searchResults
#CatalogTool.__call__ = newrelic_searchResults

newrelic.agent.initialize('newrelic.ini', 'staging')

