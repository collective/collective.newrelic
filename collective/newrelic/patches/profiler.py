from importlib import import_module
import newrelic.agent


def dashes(count, *strs):
    for s in strs:
        count -= len(s)
    return ''.join(['-' for i in range(count)])


def load_class(fqc, **kwds):
    """ Load a class by its fully qualified classname and return it. """
    try:
        mod_name, klass_name = fqc.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise Exception(('Error importing module {0}: "{1}"'.format(mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise Exception(('Module "{0}" does not define a "{1}" class'.format(mod_name, klass_name)))
    return klass


def nr_profile(profile_name, fqc, func, str_func=lambda o: o):
    klass = load_class(fqc)
    orig_func = getattr(klass, func)
    def monkeypatch(self, *args, **kwargs):
        name = str_func(self)
#        print "--- {0}".format(name)
        newrelic_monkeypatch = newrelic.agent.FunctionTraceWrapper(orig_func, name=name, group=profile_name)
        ret = newrelic_monkeypatch(self, *args, **kwargs)
        return ret
    setattr(klass, func, monkeypatch)


# In newrelic.ini
#nr_profile('Page Template', 'Products.PageTemplates.PageTemplate.PageTemplate', '__call__')
#nr_profile('DTML Method','OFS.DTMLMethod.DTMLMethod', '__call__')
##nr_profile('MLDTMLMethod','Products.MLDTML.MLDTML.MLDTMLMethod', '__call__')
#nr_profile('Z SQL Method','Products.ZSQLMethods.SQL.SQL', '__call__')
##nr_profile('Python Method','Products.PythonMethod.PythonMethod.PythonMethod', '__call__')
#nr_profile('Script (Python)','Products.PythonScripts.PythonScript.PythonScript', '_exec')

nr_profile('Filesystem Script (Python)','Products.CMFCore.FSPythonScript.FSPythonScript', '__call__',
    lambda o: o.title)
nr_profile('Filesystem DTML Method','Products.CMFCore.FSDTMLMethod.FSDTMLMethod', '__call__',
    lambda o: o.name())
nr_profile('Filesystem Page Template','Products.CMFCore.FSPageTemplate.FSPageTemplate', '__call__',
    lambda o: o.title)
nr_profile('Zope/TAL','zope.tal.talinterpreter.TALInterpreter', '__call__',
    lambda o: o.program[2][1].split('/')[-1])
nr_profile('ActionInformation','Products.CMFCore.ActionInformation.ActionInfo', '__getitem__',
    lambda o: o.data['title'])
nr_profile('ActionsTool','Products.CMFCore.ActionsTool.ActionsTool', '__call__')
nr_profile('IPortletManager','plone.portlets.interfaces.IPortletManager', '__call__')

for f in [
#        'do_version',
#        'do_mode',
#        'do_setSourceFile',
#        'do_setPosition',
#        'do_startEndTag',
#        'do_startTag',
#        'do_optTag_tal',
#        'do_rawtextBeginScope_tal',
#        'do_beginScope_tal',
#        'do_endScope',
#        'do_setLocal_tal',
#        'do_beginI18nContext',
#        'do_endI18nContext',
#        'do_insertText_tal',
#        'do_insertI18nText_tal',
#        'do_i18nVariable',
#        'do_insertTranslation',
#        'do_insertStructure_tal',
#        'do_insertI18nStructure_tal',
#        'do_loop_tal',
#        'do_rawtextColumn',
#        'do_rawtextOffset',
#        'do_condition',
#        'do_defineMacro',
#        'do_useMacro',
#        'do_extendMacro',
#        'do_defineSlot',
    ]:
    nr_profile('Zope/TAL','zope.tal.talinterpreter.TALInterpreter', f)
