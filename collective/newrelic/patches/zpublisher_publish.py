import ZPublisher 
from ZPublisher.Publish import (call_object, missing_name, dont_publish_class,
                                get_module_info, Retry, publish)

from ZPublisher.mapply import mapply

import newrelic.agent
import newrelic.api

original_publish = publish

def newrelic_publish(request, module_name, after_list, debug=0,
            # Optimize:
            call_object=call_object,
            missing_name=missing_name,
            dont_publish_class=dont_publish_class,
            mapply=mapply,
            ):

    application = newrelic.api.application.application()
    environ = {}

    trans = None

    if newrelic.agent.current_transaction() is None:
        trans = newrelic.api.web_transaction.WebTransaction(application,environ)
        trans.name_transaction(request['PATH_INFO'][1:], priority=1)
        trans.__enter__()

    result = original_publish(request, module_name, after_list, debug, call_object, missing_name, dont_publish_class, mapply)
    
    if trans:
        trans.__exit__(None, None, None)

    return result

ZPublisher.Publish.publish = newrelic_publish

