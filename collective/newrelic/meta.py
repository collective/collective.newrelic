# -*- coding: utf-8 -*-
"""ZCML handling, and applying patch"""

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject, PythonIdentifier
from zope.event import notify
from zope.interface import Interface, implements
from zope.schema import Int, Bool, Text
from collective.newrelic.utils import wrap_class_given_functions,\
                                      wrap_class_found_functions,\
                                      wrap_module_classes_functions,\
                                      wrap_module_functions
import interfaces
import logging
import pkg_resources
import re


log = logging.getLogger('collective.newrelic')


class INewrelicWrapDirective(Interface):
    """ZCML directive to apply a monkey patch late in the configuration cycle.
    This version replaces one object with another.
    """

    class_ = GlobalObject(title=u"The class being patched", required=False)
    module = GlobalObject(title=u"The module being patched", required=False)
    function = Text(title=u"Specific functions being patched (multiple, separated by space)", required=False)
    preconditions = Text(title=u'Preconditions (multiple, separated by space) to be satisified before applying this patch. Example: Products.LinguaPlone<=1.4.3',
                            required=False, default=u'')    
    order = Int(title=u"Execution order", required=False, default=1000)


def wrap(_context, original, class_=None, module=None,
            function=None, preconditions=u'', order=1000):
    """ZCML directive handler"""

    if class_ is None and module is None:
        raise ConfigurationError(u"You must specify 'class' or 'module'")
    if class_ is not None and module is not None:
        raise ConfigurationError(u"You must specify one of 'class' or 'module', but not both.")

    scope = class_ or module

    handler = _default_preserve_handler

    _context.action(
        discriminator=None,
        callable=_do_wrap,
        order=order,
        args=(handler, scope, function, original, repr(_context.info)))
    return


def _do_wrap(handler, scope, function, original, replacement, zcml_info):
    """Apply the monkey patch through preferred method"""

    try:
        org_dotted_name = '%s.%s.%s' % (scope.__module__, scope.__name__, original)
    except AttributeError:
        org_dotted_name = '%s.%s' % (scope.__name__, original)

    try:
        new_dotted_name = "%s.%s" % (getattr(replacement, '__module__', ''), replacement.__name__)
    except AttributeError:
        # builtins don't have __module__ and __name__
        new_dotted_name = str(replacement)

    handler_info = ''
    if handler != _default_patch:
        handler_info = " using custom handler %s" % handler

    log.debug("Monkey patching %s with %s" % (org_dotted_name, new_dotted_name,) + handler_info)

    info = {
        'zcml_info': zcml_info,
        'original': org_dotted_name,
        'replacement': new_dotted_name}

    notify(NewrelicMonkeyPatchEvent(info))
    handler(scope, original, replacement)
    return


def _default_patch(scope, original, replacement):
    """Default patch method"""

    setattr(scope, original, replacement)
    return


def _default_preserve_handler(scope, original, replacement):
    """ Default handler that preserves original method """

    OLD_NAME = '_nr_old_%s' % original

    if not hasattr(scope, OLD_NAME):
        setattr(scope, OLD_NAME, getattr(scope, original))

    setattr(scope, original, replacement)
    return


def _preconditions_matching(preconditions):
    """ Returns True if preconditions matching """

    matcher_r = re.compile(r'^(.*?)([-+!=]+)(.*)$', re.DOTALL | re.IGNORECASE | re.MULTILINE)
    version_r = re.compile(r'^([0-9]+)\.([0-9]+)\.?([0-9]?).*$', re.IGNORECASE | re.MULTILINE)
    ev = pkg_resources.Environment()

    # split all preconds
    for precond in preconditions.split():
        _p = precond.strip()
        package, op, version = matcher_r.search(_p).groups()

        # first try to get package - if not found fail silently
        dp = ev[package.strip()]
        if not dp:
            return True

        # fill versions - we assume having s/th like
        # 1.2.3a2 or 1.2a1 or 1.2.0 - look at regexp
        p_v = map(int, filter(lambda x: x and int(x) or 0, version_r.search(version).groups()))
        p_i = map(int, filter(lambda y: y and int(y) or 0, version_r.search(dp[0].version).groups()))

        if not p_v or not p_i:
            log.error('Could not patch because version not recognized. Wanted: %s, Installed: %s' % (p_v, p_i))
            return False

        # compare operators - dumb if check - could be better
        if op == '-=':
            return p_v >= p_i
        if op == '+=':
            return p_v <= p_i
        if op == '!=':
            return p_v != p_i
        if op in ['=', '==']:
            return p_v == p_i

        raise Exception('Unknown operator %s' % op)


class NewrelicMonkeyPatchEvent(object):
    """Envent raised when a monkeypatch is applied
    see interfaces.INewrelicMonkeyPatchEvent
    """

    implements(interfaces.INewrelicMonkeyPatchEvent)

    def __init__(self, mp_info):
        self.patch_info = mp_info
        return
