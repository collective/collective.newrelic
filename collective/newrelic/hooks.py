from collective.newrelic.utils import logger
from zope.browser.interfaces import IBrowserView
from zope.browserresource.interfaces import IResource
from zope.pagetemplate.interfaces import IPageTemplate
import newrelic.agent
import newrelic.api

# IPubAfterTraversal hook for naming our transactions!


def newrelic_transaction(event):

    try:
        request = event.request
        published = request.get('PUBLISHED', None)
        trans = newrelic.agent.current_transaction()

        # TODO: Better name resolvement. SimpleViewClass seems to have no reference
        # to the browserview it simplifies. Making it hard to make a proper dotted name.
        # Preffered name would be:  Products.MyProduct.browser.views.MyView
        # Now we only get the name as defined in conifure zcml, ie: "my_view"
        transname = published.__name__

        if trans:
            # We only want to track the following:
            # 1. BrowserViews (but not the resource kind ..)
            # 2. PageTemplate (/skins/*/*.pt ) being used as views
            if (IBrowserView.providedBy(published) or IPageTemplate.providedBy(published)) and not IResource.providedBy(published):
                trans.name_transaction(transname, group='Zope2', priority=1)
                newrelic.agent.add_custom_parameter('id', published.context.id)
                newrelic.agent.add_custom_parameter('absolute_url', published.context.absolute_url())
                logger.debug("Transaction: {0}".format(transname))
            else:
                # For debugging purpose
                logger.debug("NO transaction? : {0}   Browser: {1}  Resource: {2} PageTemplate: {3}".format(
                    transname,
                    IBrowserView.providedBy(published),
                    IResource.providedBy(published),
                    IPageTemplate.providedBy(published)))

    except Exception, e:
        # Log it and carry on.
        logger.exception(e)
