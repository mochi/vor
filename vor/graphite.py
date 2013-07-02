from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver

class GraphiteLineProtocol(LineReceiver):
    delimiter = '\n'
    service = None

    def connectionMade(self):
        self.service.protocol = self
        print self.transport


    def connectionLost(self, reason):
        self.service.protocol = None


    def lineReceived(self, line):
        pass


    def sendMetric(self, path, value, timestamp):
        """
        Send a single metric.
        """
        self.sendLine('%s %s %s' % (path, value, timestamp))



class GraphiteClientFactory(protocol.ReconnectingClientFactory):
    protocol = GraphiteLineProtocol

    def __init__(self, service):
        self.service = service


    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol()
        p.service = self.service
        return p
