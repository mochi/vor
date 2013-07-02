from twisted.application import service
from twisted.internet import reactor

from vor.elasticsearch import ElasticSearchNodeStatsGraphiteService
from vor.elasticsearch import ElasticSearchHealthGraphiteService
from vor.graphite import GraphiteClientFactory

application = service.Application("Test")

collector = ElasticSearchNodeStatsGraphiteService('http://localhost:9200/')
collector.setServiceParent(application)

factory = GraphiteClientFactory(collector)
reactor.connectTCP('localhost', 2003, factory)

collector = ElasticSearchHealthGraphiteService('http://localhost:9200/')
collector.setServiceParent(application)

factory = GraphiteClientFactory(collector)
reactor.connectTCP('localhost', 2003, factory)
