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

import talinterpreter

import cron4plone

import Globals

import os

# Import the configuration
from collective.newrelic import config