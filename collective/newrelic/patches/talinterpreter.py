from six import string_types
from zope.tal.talinterpreter import TALInterpreter

import newrelic.agent
from collective.newrelic.utils import logger

original_function = TALInterpreter.__call__


def monkeypatch(self):
    probable_name = self.program[2][1]
    name = "Value (non-file)"
    if isinstance(probable_name, string_types):
        name = probable_name.split('/')
        name = name[-1]

    newrelic_monkeypatch = newrelic.agent.FunctionTraceWrapper(original_function, name, 'Zope/TAL')
    newrelic_monkeypatch(self)

TALInterpreter.__call__ = monkeypatch
logger.info("Patched zope.tal.talinterpreter:TALInterpreter.__call__ with instrumentation")
