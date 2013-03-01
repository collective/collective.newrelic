from newrelic.core.application import Application, _logger, ThreadUtilizationSampler
import threading
import time

from newrelic.core.rules_engine import RulesEngine
from newrelic.core.samplers import create_samplers
from newrelic.core.stats_engine import StatsEngine
try:
    from newrelic.core._thread_utilization import ThreadUtilization
except:
    ThreadUtilization = None

from collective.newrelic.utils import logger

original__init__ = Application.__init__


def newrelic__init__(self, app_name, linked_applications=[]):

    _logger.debug('Initializing application with name %r and '
            'linked applications of %r.', app_name, linked_applications)

    self._creation_time = time.time()

    self._app_name = app_name
    self._linked_applications = sorted(set(linked_applications))

    self._process_id = None

    self._period_start = 0.0

    self._active_session = None

    self._transaction_count = 0
    self._last_transaction = 0.0

    self._harvest_count = 0

    self._merge_count = 0
    self._discard_count = 0

    self._agent_restart = 0
    self._agent_shutdown = False

    self._connected_event = threading.Event()

    self._detect_deadlock = False
    self._deadlock_event = threading.Event()

    self._stats_lock = threading.RLock()
    self._stats_engine = StatsEngine()

    self._stats_custom_lock = threading.RLock()
    self._stats_custom_engine = StatsEngine()

    # We setup empty rules engines here even though they will be
    # replaced when application first registered. This is done to
    # avoid a race condition in setting it later. Otherwise we have
    # to use unnecessary locking to protect access.

    self._rules_engine = {'url': RulesEngine([]),
            'transaction': RulesEngine([]), 'metric': RulesEngine([])}

    # Initial set of inbuilt data samplers for this application.

    self._samplers = list(create_samplers())

    self._thread_utilization = None

    if ThreadUtilization is not None:
        self._thread_utilization = ThreadUtilization()
        self._samplers.append(ThreadUtilizationSampler(
                self._thread_utilization))

    # Thread profiler and state of whether active or not.

    self._thread_profiler = None
    self._profiler_started = False
    self._send_profile_data = False

Application.__init__ = newrelic__init__
logger.info("Patched newrelic.core.application:Application.__init__ to work with RLock")
