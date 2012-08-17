__import__('pkg_resources').declare_namespace(__name__)

import newrelic.agent

# This is one is required: it creates the 'webtransaction'
import zpublisher_publish

# Deze geeft problemen met diazo
import zpublisher_mapply

import transformchains

import zope_event

import catalog_tool

try:
    newrelic.agent.initialize('newrelic.ini', 'staging')
except:
    pass





