============
Introduction
============

This package offers instrumentation for NewRelic ( http://www.newrelic.com ). Currently the catalog-tool, transformchains and zope-events are instrumented. A transform is included to support Real-User-Monitoring: it inserts small snippets of javascript at the top and bottom of the rendered pages.

============
Installation
============

You can add this egg 'collective.newrelic' to your eggs and it will pull in the 'newrelic' egg too. However, to get the scripts installed into your bin directory, you need to add this to your buildout.cfg (using mr.developer):

    sources = sources

    parts +=
        newrelic

    auto-checkout =
        collective.newrelic

    [sources]
    collective.newrelic = git git@github.com:Goldmund-Wyldebeast-Wunderliebe/collective.newrelic.git

    [newrelic]                                                                     
    recipe = zc.recipe.egg:scripts                                                 
    eggs = newrelic

    [instance]
    eggs +=
        collective.newrelic

Please note: the newrelic package needs python >= 2.5. This package will not work on Plone 3.

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

=============
Example usage
=============
In utils you find a few helper functions to wrap (parts) of your products and/or plone and/or any python module.
For example you could make a simple egg called myproduct.newrelic with only an __init__.py.
Within that file you have a '''initialize''' function, therein you use the helper functions for further wrapping.

------------------------------------------------------
Full class+function wrapping of an etire egg or module
------------------------------------------------------
    from plone.app import viewletmanager as plone_viewletmanager
    from collective.newrelic.utils import wrap_module_classes_functions
    class_function_modules = [plone_viewletmanager, ]
    wrapped_methods = wrap_module_classes_functions(class_function_modules)
    print len(wrapped_functions)

---------------------
Single class wrapping
---------------------
    from zope.tal.talinterpreter import TALInterpreter 
    from collective.newrelic.utils import wrap_class_found_functions
    wrapped_methods = wrap_class_found_functions(TALInterpreter)
    print len(wrapped_functions)    

----------------------------------------
Pin point precision wrapping of single class function
----------------------------------------
    from zope.tal.talinterpreter import TALInterpreter
    from collective.newrelic.utils import wrap_class_function
    wrapped_methods = wrap_class_function(TALInterpreter, TALInterpreter.__call__)
    print wrapped_methods
        "TALInterpreter.__call__"



============
References
============

 http://www.newrelic.com

 http://newrelic.com/docs/python/python-agent-installation


