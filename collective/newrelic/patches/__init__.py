__import__('pkg_resources').declare_namespace(__name__)

import newrelic.agent

#Patch newrelic_application to work with a threading.local for early (own thread!) lock checking
# import newrelic_application
import newrelic_transaction

# This is one is required: it creates the 'webtransaction'
import zserverpublisher

# Enable/disable as you like
import zpublisher_mapply

import transformchains

import zope_event

import catalog_tool

try:
    import five.pt
    import chameleon_patch
except ImportError:
    import talinterpreter

import cron4plone

import os

from collective.newrelic.utils import logger 


try:
# if the environment var was set, use this instead of the default (local) newrelic ini file
    config_file = os.environ.get('NEW_RELIC_CONFIG_FILE', 'newrelic.ini' )
    newrelic.agent.initialize(config_file)
    logger.info('New Relic Python Agent configuration set from %s.' % config_file)
except:
    pass
