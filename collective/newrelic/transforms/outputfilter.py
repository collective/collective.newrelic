from zope.interface import implements, Interface
from plone.transformchain.interfaces import ITransform
from plone.app.theming.interfaces import IThemingLayer
from zope.component import adapts

import newrelic.agent

import lxml
from repoze.xmliter.serializer import XMLSerializer

class NewRelic(object):
    """Outputfilter that adds NewRelic Real User Monitoring to content"""
    implements(ITransform)
    adapts(Interface, IThemingLayer)

    order = 8899  # Late, after Diazo does it's job

    def __init__(self, context=None, request=None):

        self.context = context
        self.request = request

    def transformString(self, result, encoding):
        return result

    def transformUnicode(self, result, encoding):
        return result

    def transformIterable(self, result, encoding):
        if not isinstance(result, XMLSerializer):
            return None

        trans = newrelic.agent.current_transaction()

        if trans is None:
            return None

        head = result.tree.find('head')
        if head:
            o = lxml.etree.XML(trans.browser_timing_header())
            head.insert( 0, o )

        foot = result.tree.find('body')
        if foot:
            o = lxml.etree.XML(trans.browser_timing_footer())
            foot.insert( 10000, o )

        return result

