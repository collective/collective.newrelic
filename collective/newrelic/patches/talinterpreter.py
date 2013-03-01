from zope.tal.talinterpreter import TALInterpreter

import newrelic.agent
from collective.newrelic.utils import logger

original_function = TALInterpreter.__call__


def monkeypatch(self):
    name = self.program[2][1].split('/')
    newrelic_monkeypatch = newrelic.agent.FunctionTraceWrapper(original_function, name[-1], 'Zope/TAL')
    newrelic_monkeypatch(self)

TALInterpreter.__call__ = monkeypatch
logger.info("Patched zope.tal.talinterpreter:TALInterpreter.__call__ with instrumentation")
