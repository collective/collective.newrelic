Introduction
------------

This package offers instrumentation for NewRelic ( http://www.newrelic.com ). Currently the catalog-tool, transformchains and zope-events are instrumented. A transform is included to support RUM (Real-User-Monitoring): it inserts small snippets of javascript at the top and bottom of the rendered pages. RUM does not work in the ZMI (Zope Management Interface).

Installation
------------

You can add this egg 'collective.newrelic' to your eggs and it will pull in the 'newrelic' egg too. 

[buildout]

# either pin versions as shown below...  
versions=versions

[versions]
newrelic = 2.6.0.5
repoze.xmliter = 0.5
# update to 1.0.9 on next release:
collective.newrelic = 1.0.8 

# ...or allow picked versions and risk breakage on product updates
#allow-picked-versions = true

parts +=
    newrelic    

[newrelic]
recipe = zc.recipe.egg:scripts
eggs = newrelic

[instance]
eggs +=
    collective.newrelic

# make sure newrelic itself is enabled and set the path to your newrelic.ini file
environment-vars +=
    NEW_RELIC_ENABLED true
    NEW_RELIC_CONFIG_FILE ${buildout:directory}/newrelic.ini

# when using supervisor, setting environment variables is slightly different:
#[supervisor]
#supervisord-environment=NEW_RELIC_ENABLED=true,NEW_RELIC_CONFIG_FILE=${buildout:directory}/newrelic.ini

A number of additional settings can optionally be configured using environment variables,
see https://docs.newrelic.com/docs/python/python-agent-configuration#environment-variables for details.
Customizing your newrelic.ini file is more advised though, see below.

The NEW_RELIC_ENABLED and NEW_RELIC_CONFIG_FILE variables need to be set for the newrelic agent to work though. 

Please note: the newrelic package needs python >= 2.5. This package will not work on Plone 3.

Use
---

To enable the logging to newrelic.com, create an account at newrelic.com and get your license key. Create a 'newrelic.ini' file in the root of your project. Either by copying the template from this package or the newrelic package or run ::

    $ bin/newrelic-admin generate-config YOUR-LICENSE-KEY newrelic.ini

This will create a newrelic.ini file in the current directory.

You might want to validate your generated file using ``newrelic-admin validate-config newrelic.ini``

The default profile is 'staging', this can be changed in the `__init__.py` in the patches directory. You can change the default name of 'Python Application (Staging)' in the newrelic.ini file. To get sensible database-traces change ::

    transaction_tracer.record_sql = obfuscated

to ::

    transaction_tracer.record_sql = raw
 

Example usage
=============
In utils you find a few helper functions to wrap (parts) of your products and/or plone and/or any python module.
For example you could make a simple egg called myproduct.newrelic with only an `__init__.py`.
Within that file you have a '''initialize''' function, therein you use the helper functions for further wrapping.

Full class+function wrapping of an entire module
------------------------------------------------
::

    from plone.app import viewletmanager as plone_viewletmanager
    from collective.newrelic.utils import wrap_module_classes_functions
    class_function_modules = [plone_viewletmanager, ]
    wrapped_methods = wrap_module_classes_functions(class_function_modules)
    print len(wrapped_methods)

Single class wrapping 
---------------------
:: 

    from zope.tal.talinterpreter import TALInterpreter
    from collective.newrelic.utils import wrap_class_found_functions
    wrapped_methods = wrap_class_found_functions(TALInterpreter)
    print len(wrapped_methods)

Pin point precision wrapping of single class function
-----------------------------------------------------
::

    from zope.tal.talinterpreter import TALInterpreter
    from collective.newrelic.utils import wrap_class_function
    wrapped_methods = wrap_class_function(TALInterpreter, TALInterpreter.__call__)
    print wrapped_methods
    "TALInterpreter.__call__"


Troubleshooting
===============

If you see a message ``The Python Agent is not enabled.`` in the Zope instance 
log, first check if ``NEW_RELIC_ENABLED`` environment variable was set correctly. 

If this is ok, check your ``newrelic.ini`` file and make sure the profile 
you are using (eg ``[newrelic:staging]``) has ``monitor_mode = true``.

It can also mean that the newrelic.ini cannot be found.
Make sure the path to your newrelic.ini file is correctly set 
using the ``NEW_RELIC_CONFIG_FILE`` environment variable.  

If you see a message ``A valid account license key cannot be found.``, 
check if you have a valid license key and make sure it is correctly set 
in the ``newrelic.ini`` file.

References
============

 http://www.newrelic.com

 http://newrelic.com/docs/python/python-agent-installation

 http://docs.newrelic.com/docs/python/testing-the-python-agent
