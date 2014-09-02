import newrelic.agent
from collective.newrelic.utils import logger
from chameleon.zpt.template import PageTemplate

original_function = PageTemplate.render


def monkeypatch(*args, **kw):
    name = 'unknown'
    self = args[0]
    if self and hasattr(self, 'filename'):
        name = self.filename
    newrelic_monkeypatch = newrelic.agent.FunctionTraceWrapper(
        original_function, name, 'chameleon')
    return newrelic_monkeypatch(*args, **kw)

PageTemplate.render = monkeypatch
logger.info("Patched chameleon.zpt.template.PageTemplate.render"
            "with instrumentation")
