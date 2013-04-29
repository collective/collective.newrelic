from collective.newrelic.utils import logger
from zope import event
from zope.event import subscribers
import newrelic.agent


def newrelic_notify(event):
    """ Notify all subscribers of ``event``.
    """
    for subscriber in subscribers:
        nr_relic_subscriber = newrelic.agent.FunctionTraceWrapper(subscriber, event.__class__.__name__, 'Zope/Dispatch')
        nr_relic_subscriber(event)

event.notify = newrelic_notify
logger.info("Patched zope.event:notify with instrumentation")
