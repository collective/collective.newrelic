from zope.event import *

def newrelic_notify(event):
    """ Notify all subscribers of ``event``.
    """
    for subscriber in subscribers:
        nr_relic_subscriber = newrelic.agent.FunctionTraceWrapper(subscriber, event.__class__.__name__, 'Zope/Dispatch')
        nr_relic_subscriber(event)

notify = newrelic_notify


