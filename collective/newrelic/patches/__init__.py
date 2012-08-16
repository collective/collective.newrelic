__import__('pkg_resources').declare_namespace(__name__)

import newrelic.agent
import newrelic.api.transaction
import newrelic.api.web_transaction

# This is one is required: it creates the 'webtransaction'
import zpublisher_publish

import zpublisher_mapply

import transformchains

import zope_event

import catalog_tool

newrelic.agent.initialize('newrelic.ini', 'staging')

print 'Init: newrelic agent'

