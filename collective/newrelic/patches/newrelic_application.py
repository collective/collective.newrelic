from newrelic.core.application import Application, _logger, ValueMetrics, InternalTraceContext, internal_metric
import threading
from collective.newrelic.utils import logger

# Patch the init to include our threading.local
original__init__ = Application.__init__


def patched__init__(self, app_name, linked_applications=[]):

    original__init__(self, app_name, linked_applications=[])
    self._thread_data = threading.local()

Application.__init__ = patched__init__
logger.info("Patched newrelic.core.application:Application.__init__ to work with thread.local for early lock checking")


# Patch record_transaction to use our threading.local
original_record_transaction = Application.record_transaction


def patched_record_transaction(self, data):
    """Record a single transaction against this application."""

    if not self._active_session:
        return

    if self._stats_engine.settings is None:
        return

    #If current thread already has a lock, return.
    if getattr(self._thread_data, 'has_lock', False):
        return

    # Do checks to see whether trying to record a transaction in a
    # different process to that the application was activated in.

    self.validate_process()

    internal_metrics = ValueMetrics()

    with InternalTraceContext(internal_metrics):
        try:
            # We accumulate stats into a workarea and only then merge it
            # into the main one under a thread lock. Do this to ensure
            # that the process of generating the metrics into the stats
            # don't unecessarily lock out another thread.

            stats = self._stats_engine.create_workarea()
            stats.record_transaction(data)

        except Exception:
            _logger.exception('The generation of transaction data has '
                    'failed. This would indicate some sort of internal '
                    'implementation issue with the agent. Please report '
                    'this problem to New Relic support for further '
                    'investigation.')

        with self._stats_lock:
            try:
                self._thread_data.has_lock = True

                self._transaction_count += 1
                self._last_transaction = data.end_time

                internal_metric('Supportability/Transaction/Counts/'
                        'metric_data', stats.metric_data_count())

                self._stats_engine.merge_metric_stats(stats)
                self._stats_engine.merge_other_stats(stats)

                # We merge the internal statistics here as well even
                # though have popped out of the context where we are
                # recording. This is okay so long as don't record
                # anything else after this point. If we do then that
                # data will not be recorded.
                self._stats_engine.merge_value_metrics(
                        internal_metrics.metrics())

            except Exception:
                _logger.exception('The merging of transaction data has '
                        'failed. This would indicate some sort of '
                        'internal implementation issue with the agent. '
                        'Please report this problem to New Relic support '
                        'for further investigation.')
            finally:
                self._thread_data.has_lock = False

Application.record_transaction = patched_record_transaction
logger.info("Patched newrelic.core.application:Application.record_transaction to work with thread.local for early lock checking")
