"""
Service for pulling Redis list lengths.
"""

import time

from twisted.application import service
from twisted.internet import defer, task
from twisted.python import log

from txredis.client import RedisClientFactory

from vor.graphite import sanitizeMetricElement

class RedisGraphiteService(service.Service):
    """
    Redis list lenght poller service.

    This retrieves the lists matching L{keysPattern} and retrieves the list
    lenghts to post to Graphite.
    """

    def __init__(self, reactor, host, port, keysPattern):
        """
        @param keysPattern: Pattern of keys to poll the list length for.
        """
        self.reactor = reactor
        self.host = host
        self.port = port
        self.keysPattern = keysPattern

        self.factory = RedisClientFactory()
        self.connector = None
        self.basePath = "redis.{}.list.".format(sanitizeMetricElement(host))
        self.lc = task.LoopingCall(self.poll)


    def startService(self):
        """
        Start connecting to the Redis server and start polling.
        """
        service.Service.startService(self)
        self.factory.resetDelay()
        self.connector = self.reactor.connectTCP(self.host, self.port,
                                                 self.factory)
        self.lc.start(10)


    def stopService(self):
        """
        Disconnect from the Redis server and stop polling.
        """
        if self.lc.running:
            self.lc.stop()

        if self.connector is not None:
            self.factory.stopTrying()
            self.connector.disconnect()
            self.connector = None


    def sendMetric(self, length, key):
        path = self.basePath + key.replace(':', '.') + '.length'
        self.protocol.sendMetric(path, length, time.time())


    def getListLengths(self, keys):
        dl = []
        for key in keys:
            d = self.factory.client.llen(key)
            d.addCallback(self.sendMetric, key)
            d.addErrback(log.err)
            dl.append(d)

        return defer.gatherResults(dl)


    def poll(self):
        if not self.factory.client:
            return None

        d = self.factory.client.keys(self.keysPattern)
        d.addCallback(self.getListLengths)
        return d
