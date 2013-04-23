from collective.newrelic.utils import logger
from Products.Five.browser.resource import ResourceFactory
import newrelic.agent
import newrelic.api


original__call__ = ResourceFactory.__call__


def patched__call__(self, *args, **kwargs):
    resource = original__call__(self, *args, **kwargs)
    trans = newrelic.agent.current_transaction()
    trans_name = trans.name
    trans.name_transaction(trans_name, group="Resource", priority=2)
    return resource


ResourceFactory.__call__ = patched__call__
logger.info("Patched Products.Five.browser.resource:ResourceFactory.__call__ to add transaction group")
