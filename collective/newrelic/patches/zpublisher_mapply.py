import ZPublisher
from ZPublisher.mapply import (default_missing_name, default_handle_class)

import newrelic.agent
import newrelic.api

original_mapply = ZPublisher.mapply.mapply

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

ZPublisher.mapply.mapply = newrelic_mapply


