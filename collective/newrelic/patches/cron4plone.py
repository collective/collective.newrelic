HAS_CRON4PLONE = False
import newrelic.agent
from collective.newrelic.utils import logger
try:
    from Products.cron4plone.browser.views.cron_tick import CronTick
    HAS_CRON4PLONE = True
except ImportError, e:
    # Doesn't have it!
    pass


if HAS_CRON4PLONE:

    original_tick = CronTick.tick

    @newrelic.agent.background_task(name='crontick')
    def patched_tick(self, *args, **kwargs):
        original_tick(self, *args, **kwargs)

    CronTick.tick = patched_tick
    logger.info("Patched Products.cron4plone.browser.CronTick:tick to become a background task")
else:
    logger.inofo("Unable to patched Products.cron4plone, probably not used.")
