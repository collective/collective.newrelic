import inspect
import newrelic.agent
import logging
logger = logging.getLogger('collective.newrelic')


def newrelic_wrapper(our_class, orig_func, newrelic_label):
    """Newrelic wrapper for given class/module and function.
    Params:
        our_class       :: class or module
        orig_func       :: actual function
        newrelic_label  :: Our nice newrelic_label

        This function wraps the given function with a newrelic one.
        We monkeypatch the shit out of it...
    """

    # Function name
    func_name = orig_func.__name__

    # We sometimes return with an already wrapped function
    if func_name == 'newrelic_function_wrapper':
        #GTFO!
        return

    # Prefix the func_name and set it
    orig_func_name = "original_{0}".format(func_name)
    setattr(our_class, orig_func_name, orig_func)

    # Some 'label' stuff for newrelic statistics
    # For module/class we want slightly different output
    # Module output:   module_name:function_name
    # Class output:    module_name:ClassName.function_name
    if inspect.ismodule(our_class):
        mod_name = our_class.__name__
        class_name = ""
    else:
        mod_name = our_class.__module__
        class_name = "{0}.".format(our_class.__name__)

    # Our generic wrapper, one size fits all.
    def newrelic_function_wrapper(self, *args, **kwargs):
        trans = newrelic.agent.current_transaction()
        outputlabel = "{0}:{1}{2}".format(mod_name, class_name, func_name)
        with newrelic.agent.FunctionTrace(trans, outputlabel, newrelic_label):
            result = getattr(our_class, orig_func_name)(self, *args, **kwargs)
        return result

    # Monkey patch and report
    setattr(our_class, func_name, newrelic_function_wrapper)
    logger.info("{0}:{1}{2} wrapped".format(mod_name, class_name, func_name))


# Helper functions for collection


def get_classes(mod, mod_name, classes=[]):
    """ Recursively collect all the classes in the module module."""
    for name, obj in inspect.getmembers(mod):
        if inspect.ismodule(obj) and mod_name in obj.__name__:
            classes = get_classes(obj, mod_name, classes)
        if inspect.isclass(obj) and mod_name in obj.__module__:
            classes.append(obj)
    return classes


def get_module_functions(mod, mod_name, functions=[]):
    """ This recursive function gets the fuctions of a module and it's children modules. """
    for name, obj in inspect.getmembers(mod):
        if inspect.ismodule(obj) and mod_name in obj.__name__:
            functions = get_module_functions(obj, mod_name, functions)
        elif (inspect.isfunction(obj) or inspect.ismethod(obj)) and mod_name in obj.__module__:
            functions.append((mod, obj))
    return functions
# END OF: Helper functions for collection


# Various wrap functions


def wrap_class_function(klass, funktion, newrelic_label="Zope/", wrapped_methods=[]):
    """Wrap a single function of a single klass with newrelic. The most basic way"""
    klass_module = klass.__module__
    #Make a nice wrapped name for the method (module:class.function)
    wrapped_name = "{0}:{1}.{2}".format(klass_module, klass.__name__, funktion.__name__)
    if wrapped_name not in wrapped_methods:

        #Wrap me long time
        newrelic_wrapper(klass, funktion, newrelic_label)
        wrapped_methods.append(wrapped_name)

    return wrapped_methods


def wrap_class_given_functions(klass, funktions=[], newrelic_label="Zope/", wrapped_methods=[]):
    """ Wrap the given functions of the given klass with newrelic """
    for funk in funktions:
        wrapped_methods = wrap_class_function(klass, funk, newrelic_label, wrapped_methods)

    return wrapped_methods


def wrap_class_found_functions(klass, newrelic_label="Zope/", wrapped_methods=[]):
    """Wrap all the functions we find in the given class """

    # Go over any attributes we found, see if they are function or methods.
    for name in klass.__dict__.keys():
        attr = getattr(klass, name)

        #Determine if type is function/method
        #TODO: What is the exact difference?!
        #TODO: See if the 'newrelic' 'memogetter' exclusions are still needed

        if (inspect.isfunction(attr) \
            or inspect.ismethod(attr)) \
            and not 'newrelic' in name \
            and not 'memogetter' in name:

            wrapped_methods = wrap_class_function(klass, attr, newrelic_label, wrapped_methods)
    return wrapped_methods


def wrap_module_classes_functions(module_list=[], newrelic_label="Zope/", wrapped_methods=[]):
    """ Recursively loop over given module list and wrap any class-level functions found.
        Return a list of wrapped methods to prevent further wrapping """

    for the_module in module_list:

        # Recursively get all the classes in this module and the modules within
        the_classes = get_classes(the_module, the_module.__name__)

        # Go over the classes we found
        for the_class in the_classes:

            # Go over any attributes we found, see if they are function or methods.
            for name in the_class.__dict__.keys():
                attr = getattr(the_class, name)

                #Determine if type is function/method
                #TODO: What is the exact difference?!
                #TODO: See if the 'newrelic' 'memogetter' exclusions are still needed

                if (inspect.isfunction(attr) \
                    or inspect.ismethod(attr)) \
                    and not 'newrelic' in name \
                    and not 'memogetter' in name:

                    wrapped_methods = wrap_class_function(the_class, attr, newrelic_label, wrapped_methods)
    return wrapped_methods


def wrap_module_functions(module_list=[], newrelic_label="Zope/", wrapped_methods=[]):
    """ Recursively loop over the given module list and wrap any module-level functions found.
        Return a list of wrapped_methods to prevent further wrapping """
    for the_module in module_list:

        #Get a tuple-filled list of all function is this module and it's submodules
        module_functions = get_module_functions(the_module, the_module.__name__)
        for (modul, func) in module_functions:

            #Make a nice wrapped name for the method (module:function)
            wrapped_name = "{0}:{1}".format(modul.__name__, func.__name__)
            if wrapped_name not in wrapped_methods:

                #Wrap me long time.
                newrelic_wrapper(modul, func, newrelic_label)
                wrapped_methods.append(wrapped_name)

    return wrapped_methods
