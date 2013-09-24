"""
ElasticSearch stats poller that sends statistics to Graphite.
"""

import simplejson
import time

from twisted.application import service
from twisted.internet import task
from twisted.python import log
from twisted.web.client import getPage

class BaseElasticSearchGraphiteService(service.Service):
    """
    Base service for polling ElasticSearch stats to send to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}

    @ivar interval: The interval time between polling.
    @type interval: C{int}
    """
    interval = 5
    suffixes = ()
    API = None

    def __init__(self, baseURL):
        """
        @param baseURL: Base URL of the ElasticSearch API, including trailing
            slash.
        """
        self.endpoint = baseURL + self.API
        self.protocol = None


    def _flattenValue(self, data, value, prefix, key, timestamp):
        key = key.replace(' ', '')
        flatKey = "%s.%s" % (prefix, key)
        if hasattr(value, 'upper'):
            # Skip strings unless they have suffixed counterparts with a
            # metric.
            for suffix in self.suffixes:
                suffixedKey = key + suffix
                if suffixedKey in data:
                    self.sendMetric(flatKey, data[suffixedKey], timestamp)
                    break
        elif hasattr(value, 'iteritems'):
            # Dicts are flattened.
            self._flattenDict(value, flatKey, timestamp)
        elif hasattr(value, 'index'):
            # Give each item in a sequence their own index and flatten the
            # value.
            index = 0
            for item in value:
                self._flattenValue(None, item, flatKey, '%d' % index,
                                   timestamp)
                index += 1
        else:
            # A regular metric.
            self.sendMetric(flatKey, value, timestamp)


    def _flattenDict(self, data, prefix, timestamp):
        if 'timestamp' in data:
            timestamp = data['timestamp'] / 1000.

        for key, value in data.iteritems():
            if (key.endswith(self.suffixes) or
                key == 'timestamp'):
                continue
            else:
                self._flattenValue(data, value, prefix, key, timestamp)


    def sendMetric(self, path, value, timestamp):
        if self.protocol:
            self.protocol.sendMetric(path, float(value), timestamp)


    def collectStats(self):
        d = getPage(self.endpoint)
        d.addCallback(simplejson.loads)
        d.addCallback(self.flatten)
        d.addErrback(log.err)
        return d


    def startService(self):
        self.call = task.LoopingCall(self.collectStats)
        self.call.start(self.interval, now=False)


    def stopService(self):
        self.call.stop()



class ElasticSearchNodeStatsGraphiteService(BaseElasticSearchGraphiteService):
    """
    Service that polls ElasticSearch node stats and sends them to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}
    """

    suffixes = ('_in_bytes', '_in_millis')
    API = '_cluster/nodes/stats?all=1'

    def flatten(self, data):
        for node in data['nodes'].itervalues():
            name = node['name']
            timestamp = node['timestamp']

            prefix = 'es.nodes.'+ name
            if ('attributes' in node and
                node['attributes'].get('data', 'true') != 'true'):
                del node['indices']
            self._flattenDict(node, prefix, timestamp)



class ElasticSearchHealthGraphiteService(BaseElasticSearchGraphiteService):
    """
    Service that polls ElasticSearch cluster health and sends it to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}
    """

    API = '_cluster/health'

    def flatten(self, data):
        timestamp = time.time()
        prefix = 'es.cluster'

        # Make separate metrics for each status

        status = {'green': 0,
                  'yellow': 0,
                  'red': 0}
        status[data['status']] = 1

        data['status'] = status
        self._flattenDict(data, prefix, timestamp)
