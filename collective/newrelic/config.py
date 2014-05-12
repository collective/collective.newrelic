import newrelic.agent
import os
from collective.newrelic.utils import logger 

CONFIG_LOADED = False
try:
    if not CONFIG_LOADED:
    # if the environment var was set, use this instead of the default (local) newrelic ini file
        config_file = os.environ.get('NEW_RELIC_CONFIG_FILE', 'newrelic.ini' )
        newrelic.agent.initialize(config_file)
        logger.info('New Relic Python Agent configuration set from %s.' % config_file)
        CONFIG_LOADED = True
except:

    pass