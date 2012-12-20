__import__('pkg_resources').declare_namespace(__name__)

import newrelic.agent

# This is one is required: it creates the 'webtransaction'
import zpublisher_publish

# Enable/disable as you like

import zpublisher_mapply

import transformchains

import zope_event

import catalog_tool

import talinterpreter

try:
    newrelic.agent.initialize('newrelic.ini', 'development')
except:
    pass





