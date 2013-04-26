from collective.newrelic.utils import logger
from zope.browser.interfaces import IBrowserView
from zope.component import adapter
from ZPublisher.interfaces import IPubAfterTraversal
import newrelic.agent
import newrelic.api

def newrelic_transaction(event):
    
    try:                                               
        request = event.request
        published = request.get('PUBLISHED', None)
        trans = newrelic.agent.current_transaction()
        transname = published.__name__

        # TODO: Better name resolvement. SimpleViewClass seems to have no reference
        # to the browserview it simplifies. Making it hard to make a proper dotted name.
        # Preffered name would be:  Products.MyProduct.browser.views.MyView
        # Now we only get the name as defined in conifure zcml, ie: "my_view"

        if IBrowserView.providedBy(published) and trans:
            transname = published.__name__
            trans.name_transaction(transname, group='Zope2', priority=1)
            logger.info("Named a transaction: {0}".format(transname))

    except Exception, e:
        logger.exception(e)