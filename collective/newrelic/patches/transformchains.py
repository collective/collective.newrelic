from six import text_type
from six import binary_type
from operator import attrgetter
from plone.transformchain.transformer import (
    LOGGER,
    Transformer,
)
from ZODB.POSException import ConflictError
from zope.component import getAdapters
try:
    from ZServer.FTPRequest import FTPRequest
except ImportError:
    FTPRequest = type(None)
from plone.transformchain.interfaces import DISABLE_TRANSFORM_REQUEST_KEY
from plone.transformchain.interfaces import ITransform

import newrelic.agent
from collective.newrelic.utils import logger

#Save original for further use.
original_transform_call = Transformer.__call__


def newrelic_transform__call__(self, request, result, encoding):

    # Don't transform FTP requests
    if isinstance(request, FTPRequest):
        return None

    # Off switch
    if request.environ.get(DISABLE_TRANSFORM_REQUEST_KEY, False):
        return None

    try:
        published = request.get('PUBLISHED', None)

        handlers = [
            v[1] for v in getAdapters((published, request,), ITransform)
        ]
        handlers.sort(key=attrgetter('order'))

        trans = newrelic.agent.current_transaction()

        for handler in handlers:
            with newrelic.agent.FunctionTrace(handler.__class__.__name__, 'Zope/Transform'):

                if isinstance(result, text_type):
                    newResult = handler.transformUnicode(result, encoding)
                elif isinstance(result, binary_type):
                    newResult = handler.transformBytes(result, encoding)
                else:
                    newResult = handler.transformIterable(result, encoding)

                if newResult is not None:
                    result = newResult

        return result
    except ConflictError:
        raise
    except Exception as e:
        LOGGER.exception(u"Unexpected error whilst trying to apply transform chain")

Transformer.__call__ = newrelic_transform__call__
logger.info("Patched plone.transformchain.transformer:Transformer.__call__ with instrumentation")
