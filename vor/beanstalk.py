"""
Service for pulling Beanstalk stats.
"""

from __future__ import absolute_import

import time

from twisted.application import service
from twisted.internet import defer, protocol, task
from twisted.python import log

from vor.graphite import sanitizeMetricElement

import beanstalk

class BeanstalkFactory(protocol.ReconnectingClientFactory):

    protocol = beanstalk.twisted_client.Beanstalk
    client = None

    def buildProtocol(self, addr):
        p = protocol.ReconnectingClientFactory.buildProtocol(self, addr)
        self.client = p
        return p



class BeanstalkGraphiteService(service.Service):
    """
    Beanstalk stats poller service.

    This retrieves the global stats and the stats of all tubes and posts
    the stats to graphite.
    """

    def __init__(self, reactor, host, port):
        self.reactor = reactor
        self.host = host
        self.port = port

        self.factory = BeanstalkFactory()
        self.connector = None
        self.basePath = "beanstalk.{}".format(sanitizeMetricElement(host))
        self.lc = task.LoopingCall(self.poll)


    def startService(self):
        """
        Start connecting to the Beanstalk server and start polling.
        """
        service.Service.startService(self)
        self.factory.resetDelay()
        self.connector = self.reactor.connectTCP(self.host, self.port,
                                                 self.factory)
        self.lc.start(10)


    def stopService(self):
        """
        Disconnect from the Beanstalk server and stop polling.
        """
        if self.lc.running:
            self.lc.stop()

        if self.connector is not None:
            self.factory.stopTrying()
            self.connector.disconnect()
            self.connector = None


    def sendMetrics(self, stats, prefix):
        for key, value in stats.iteritems():
            try:
                float(value)
            except (TypeError, ValueError):
                continue

            if key in ('version', 'pid'):
                continue

            path = '%s.%s' % (prefix, key)
            self.protocol.sendMetric(path, value, time.time())


    def gotStats(self, result, prefix):
        stats = result['data']
        self.sendMetrics(stats, prefix)


    def getTubeStats(self, tubes):
        dl = []
        for tube in tubes:
            d = self.factory.client.stats_tube(tube)
            d.addCallback(self.gotStats, '%s.tube.%s' % (self.basePath, tube))
            d.addErrback(log.err)
            dl.append(d)

        return defer.gatherResults(dl)


    def getTubes(self, bs):
        d = bs.list_tubes()
        d.addCallback(lambda result: result['data'])
        d.addCallback(self.getTubeStats)
        d.addCallback(lambda _: bs)
        return d


    def getGlobalStats(self, bs):
        d = bs.stats()
        d.addCallback(self.gotStats, '%s.server' % self.basePath)
        d.addCallback(lambda _: bs)
        return d

    def poll(self):
        bs = self.factory.client
        if not bs:
            return None

        d = self.getGlobalStats(bs)
        d.addCallback(self.getTubes)
        d.addErrback(log.err)
        return d
