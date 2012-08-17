============
Introduction
============

This package offers instrumentation for NewRelic ( http://www.newrelic.com ). Currently the catalog-tool, transformchains and zope-events are instrumented. A transform is included to support Real-User-Monitoring: it inserts small snippets of javascript at the top and bottom of the rendered pages.

============
Installation
============

You can add this egg 'collective.newrelic' to your eggs and it will pull in the 'newrelic' egg too. However, to get the scripts installed into your bin directory, you need to add this to your buildout.cfg:

parts +=
    newrelic

[newrelic]                                                                     
recipe = zc.recipe.egg:scripts                                                 
eggs = newrelic 


============
Use
============

To enable the logging to newrelic.com, create an account at newrelic.com and get your license key. Create a 'newrelic.ini' file in the root of your project. Either by copying the template from this package or the newrelic package or run:

$ bin/newrelic-admin generate-config YOUR-LICENSE-KEY newrelic.ini 

This will create a newrelic.ini file in the current directory.

The default profile is 'staging', this can be changed in the __init__.py in the patches directory. You can change the default name of 'Python Application (Staging)' in the newrelic.ini file. To get sensible database-traces change

    transaction_tracer.record_sql = obfuscated

to

    transaction_tracer.record_sql = raw

============
References
============

 http://www.newrelic.com

 http://newrelic.com/docs/python/python-agent-installation


