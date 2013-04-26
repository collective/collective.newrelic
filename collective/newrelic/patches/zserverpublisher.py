
from ZServer.PubCore.ZServerPublisher import ZServerPublisher
import newrelic.agent
import newrelic.api

import newrelic.api.transaction
import newrelic.api.web_transaction
import logging

LOG = logging.getLogger('ZServerPublisher')
original__init__ = ZServerPublisher.__init__
from collective.newrelic.utils import logger

PLACEHOLDER = "PLACEHOLDER"

def newrelic__init__(self, accept):
    from sys import exc_info
    from ZPublisher import publish_module
    from ZPublisher.WSGIPublisher import publish_module as publish_wsgi
    trans = None
    while 1:
        try:
            name, a, b = accept()
            if name == "Zope2":

                try:
                    application = newrelic.api.application.application_instance()
                    environ = {}
                    trans = newrelic.api.web_transaction.WebTransaction(application, environ)
                    trans.name_transaction(PLACEHOLDER, group='Zope2', priority=1)
                    trans.__enter__()

                    publish_module(
                        name,
                        request=a,
                        response=b)
                finally:
                    b._finish()
                    if trans:
                        if trans.name == 'PLACEHOLDER':
                            newrelic.agent.ignore_transaction()
                        trans.__exit__(None, None, None)
                    a = b = None

            elif name == "Zope2WSGI":
                try:
                    res = publish_wsgi(a, b)
                    for r in res:
                        a['wsgi.output'].write(r)
                finally:
                    # TODO: Support keeping connections open.
                    a['wsgi.output']._close = 1
                    a['wsgi.output'].close()
        except:
            LOG.error('exception caught', exc_info=True)


ZServerPublisher.__init__ = newrelic__init__
logger.info("Patched ZServer.PubCore.ZServerPublisher:ZServerPublisher.__init__ with WebTransaction creation, entering and exiting")
