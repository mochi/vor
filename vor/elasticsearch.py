"""
ElasticSearch stats poller that sends statistics to Graphite.
"""

import time

from twisted.application import service
from twisted.internet import task
from twisted.internet.ssl import CertificateOptions
from twisted.python import log
from twisted.web.iweb import IPolicyForHTTPS

import treq

from zope.interface import implementer

from vor.graphite import sanitizeMetricElement

@implementer(IPolicyForHTTPS)
class _NoVerifyContextFactory(object):
    """
    Context that doesn't verify SSL connections.
    """
    def creatorForNetloc(self, hostname, port):
        return CertificateOptions(verify=False)


def _noVerifyAgent( *args, **kwargs ):
    """Agent that suppresses TLS verification

    treq.get(..., agent=_noVerifyAgent())

    Returns the same agent every time...
    """
    if getattr(_noVerifyAgent, 'agent',None) is None:
        from treq import api
        reactor = api.default_reactor(kwargs.get('reactor'))
        pool = api.default_pool(reactor,
                            kwargs.get('pool'),
                            kwargs.get('persistent'))
        _noVerifyAgent.agent = api.Agent(
            reactor,
            contextFactory=_NoVerifyContextFactory(),
            pool=pool
        )
    return _noVerifyAgent.agent


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

    def __init__(self, baseURL, prefix='es', auth=None):
        """
        @param baseURL: Base URL of the ElasticSearch API, including trailing
            slash.
        """
        self.endpoint = baseURL + self.API
        self.prefix = prefix
        self.auth = auth

        self.protocol = None
        self.treq = treq.client.HTTPClient(_noVerifyAgent())


    def _flattenValue(self, data, value, prefix, key, timestamp):
        key = "%s.%s" % (prefix, key)
        flatKey = key.replace(' ', '')
        if hasattr(value, 'upper'):
            return
        elif hasattr(value, 'iteritems'):
            self._flattenDict(value, flatKey, timestamp)
        elif hasattr(value, 'index'):
            self._flattenSequence(value, flatKey, timestamp)
        elif value is not None:
            # A regular metric.
            self.sendMetric(flatKey, value, timestamp)


    def _flattenSequence(self, data, prefix, timestamp):
        """
        Give each item in a sequence their own index and flatten the value.
        """
        index = 0
        for item in data:
            self._flattenValue(None, item, prefix, '%d' % index,
                               timestamp)
            index += 1


    def _flattenDict(self, data, prefix, timestamp):
        if 'timestamp' in data:
            timestamp = data['timestamp'] / 1000.

        for key, value in data.iteritems():
            if key == 'timestamp':
                continue

            if key.endswith(self.suffixes):
                for suffix in self.suffixes:
                    if key.endswith(suffix):
                        key = key[:-len(suffix)]

            self._flattenValue(data, value, prefix, key, timestamp)


    def sendMetric(self, path, value, timestamp):
        if self.protocol:
            self.protocol.sendMetric(path, float(value), timestamp)


    def collectStats(self):
        d = self.treq.get(self.endpoint, auth=self.auth)
        d.addCallback(treq.json_content)
        d.addCallback(self.flatten)
        d.addErrback(log.err)
        return d


    def startService(self):
        self.call = task.LoopingCall(self.collectStats)
        self.call.start(self.interval, now=False)


    def stopService(self):
        self.call.stop()



class ElasticSearchStatsGraphiteService(BaseElasticSearchGraphiteService):
    """
    Service that polls ElasticSearch cluster stats and sends them to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}
    """

    suffixes = ('_in_bytes', '_in_millis')
    API = '_cluster/stats'

    def flatten(self, data):
        timestamp = data['timestamp']

        prefix = '%s.cluster' % (self.prefix,)
        self._flattenDict(data, prefix, timestamp)


    def _flattenSequence(self, data, prefix, timestamp):
        """
        Ignore lists, as those represent mostly static data.
        """
        pass



class ElasticSearchNodeStatsGraphiteService(BaseElasticSearchGraphiteService):
    """
    Service that polls ElasticSearch node stats and sends them to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}
    """

    suffixes = ('_in_bytes', '_in_millis')
    API = '_nodes/stats'

    def __init__(self, *args, **kwargs):
        self.hostname_only = kwargs.pop('hostname_only', False)
        if type(self) != self.__class__:
            # we're using an old version of Twisted that uses old style classes
            BaseElasticSearchGraphiteService.__init__(self, *args, **kwargs)
        else:
            super(ElasticSearchNodeStatsGraphiteService, self).__init__(*args, **kwargs)

    def flatten(self, data):
        for node in data['nodes'].itervalues():
            name = node['name']
            if self.hostname_only:
                name = name.split('.')[0]
            timestamp = node['timestamp']

            prefix = '%s.nodes.%s' % (self.prefix, name)
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
        prefix = '%s.cluster' % (self.prefix,)

        # Make separate metrics for each status

        status = {'green': 0,
                  'yellow': 0,
                  'red': 0}
        status[data['status']] = 1

        data['status'] = status
        self._flattenDict(data, prefix, timestamp)


class ElasticSearchIndicesStatsGraphiteService(BaseElasticSearchGraphiteService):
    """
    Service that polls ElasticSearch indices stats and send them to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}
    """
    suffixes = ('_in_bytes', '_in_millis')
    API = '_stats'

    def flatten(self, data):
        timestamp = time.time()
        for name, index in data['indices'].iteritems():
            prefix = '%s.indices.%s' % (self.prefix,
                                        sanitizeMetricElement(name))
            self._flattenDict(index, prefix, timestamp)


class ElasticSearchIndexStatsGraphiteService(BaseElasticSearchGraphiteService):
    """
    Service that polls ElasticSearch index stats and sends them to Graphite.

    @ivar protocol: The Graphite protocol.
    @type protocol: L{vor.graphite.GraphiteLineProtocol}
    """
    # XXX deprecated in ES 1.2.0 and removed in ES 2.0.

    suffixes = ('_in_bytes', '_in_millis')
    API = '_status'

    def flatten(self, data):
        timestamp = time.time()
        for name, index in data['indices'].iteritems():
            prefix = '%s.indices.%s' % (self.prefix,
                                        sanitizeMetricElement(name))
            self._flattenDict(index, prefix, timestamp)
