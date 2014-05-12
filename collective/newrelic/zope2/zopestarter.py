from collective.newrelic.utils import logger
import newrelic.agent
import newrelic.api
import newrelic.api.web_transaction
import Zope2.Startup

# Save original
_original_prepare = Zope2.Startup.ZopeStarter.prepare

STARTUP = 'starting-plone'

def newrelic_prepare(self, *args, **kwargs):
    print "Newrelic: Start of startup transaction"

    # Prepare the app and transaction
    application = newrelic.api.application.application_instance()
    environ = {'newrelic.enabled':True} #TODO: Needed?
    trans = newrelic.api.web_transaction.WebTransaction(application, environ)
    trans.name_transaction(STARTUP, group='Zope2', priority=1)
    trans.__enter__()

    # Call the original prepare
    _original_prepare(self, *args, **kwargs)
    if trans:
        trans.__exit__(None, None, None)
        print "Newrelic: End of startup transaction"


Zope2.Startup.ZopeStarter.prepare = newrelic_prepare
logger.info("Patched Zope2.Startup.ZopeStart.prepare with instrumentation to exit startup transaction")
print("collective.newrelic: Patched Zope2.Startup.ZopeStart.prepare with instrumentation to exit startup transaction")