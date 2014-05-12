import Zope2.Startup

import newrelic.agent
import newrelic.api

import newrelic.api.transaction
import newrelic.api.web_transaction

from collective.newrelic.utils import logger
_original_prepare = Zope2.Startup.ZopeStarter.prepare

STARTUP = 'starting-plone'

def newrelic_prepare(self, *args, **kwargs):
    print "Newrelic: Start of startup transaction"
    application = newrelic.api.application.application_instance()
    environ = {'newrelic.enabled':True}
    trans = newrelic.api.web_transaction.WebTransaction(application, environ)
    trans.name_transaction(STARTUP, group='Zope2', priority=1)
    trans.__enter__()
    _original_prepare(self, *args, **kwargs)
    if trans:
        trans.__exit__(None, None, None)
        print "Newrelic: End of startup transaction"


Zope2.Startup.ZopeStarter.prepare = newrelic_prepare
logger.info("Patched Zope2.Startup.ZopeStart.prepare with instrumentation to exit startup transaction")
print("collective.newrelic: Patched Zope2.Startup.ZopeStart.prepare with instrumentation to exit startup transaction")