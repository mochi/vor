import re

from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver

def sanitizeMetric(name):
    """
    Sanitize (part of) a metric name.

    A Graphite metric path consists of one or more elements separated by
    dots (C{.}). This takes a name and returns the sanitized version as a
    byte string. Whitespace is replaced by an underscore (C{_}), slashes
    (usually used as file system path separators) are replaced by dashes
    (C{-}), and characters other than ASCII letters, digits, dashes,
    underscores, and dots are removed.

    Note that this does not touch dots. If you want to use hostnames as a
    single element in a metric name, use L{sanitizeMetricElement} instead.

    @param name: Metric name to be sanitized.
    @type name: C{str}

    @rtype: C{bytes}
    """
    name = re.sub('\s+', '_', name)
    name = re.sub('\/', '-', name)
    name = re.sub('[^a-zA-Z_\-0-9\.]', '', name)
    return name.encode('ascii')



def sanitizeMetricElement(element):
    """
    Sanitize an string to be used as a metric name element.

    This replaces dots in strings with underscores and then
    calls L{sanitizeMetric} before returning the result. This can be used to
    use hostnames as a single element in a metric name.

    @rtype: C{bytes}
    """
    return sanitizeMetric(element.replace('.', '_'))



class GraphiteLineProtocol(LineReceiver):
    delimiter = '\n'
    service = None

    def connectionMade(self):
        self.service.protocol = self


    def connectionLost(self, reason):
        self.service.protocol = None


    def lineReceived(self, line):
        pass


    def sendMetric(self, path, value, timestamp):
        """
        Send a single metric.
        """
        self.sendLine('%s %s %s' % (path.encode('utf-8'), value, timestamp))



class GraphiteClientFactory(protocol.ReconnectingClientFactory):
    protocol = GraphiteLineProtocol

    def __init__(self, service):
        self.service = service


    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol()
        p.service = self.service
        return p


class FakeGraphiteProtocol(object):
    """
    Fake protocol that stores each metric indexed by metric path.
    """
    def __init__(self):
        self.output = {}


    def sendMetric(self, path, value, timestamp):
        self.output[path] = (value, timestamp)
