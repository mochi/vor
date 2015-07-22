"""
Tests for L{vor.kafka}.
"""

from twisted.trial import unittest

from vor.graphite import FakeGraphiteProtocol
from vor.kafka import parseOffsets
from vor.kafka import KafkaError, KafkaNoTopicError, KafkaGraphiteService

class ParseOffsetsTests(unittest.TestCase):

    def test_success(self):
        """
        A success result can be parsed into offsets.
        """
        text = """Group           Topic                          Pid Offset          logSize         Lag             Owner
group1 events                0   734982565       734982587       22              group1_consumer.example.org-1436585515700-8c4fbc41-0
group1 events                1   824687291       824687314       23              group1_consumer.example.org-1436585515700-8c4fbc41-0
group1 events                2   551840658       551840689       31              group1_consumer.example.org-1436596330605-29002ae5-0
"""

        result = parseOffsets(text)
        self.assertEqual(3, len(result))
        self.assertEqual(22, result[0]['lag'])
        self.assertEqual(824687291, result[1]['offset'])
        self.assertEqual(551840689, result[2]['logSize'])
        self.assertEqual('group1_consumer.example.org-1436596330605-29002ae5-0',
                         result[2]['owner'])


    def test_newPartitions(self):
        """
        New topic partitions for consumer groups without current consumers
        have None for the consumer lag and offset fields.
        """
        text = """Group           Topic                          Pid Offset          logSize         Lag             Owner
group1 events                0   734982565       734982587       22              none
group1 events                1   824687291       824687314       23              none
group1 events                2   -1       551840689       unknown              none
"""

        result = parseOffsets(text)
        self.assertIdentical(None, result[2]['offset'])
        self.assertIdentical(None, result[2]['lag'])
        self.assertIdentical(None, result[2]['owner'])


    def test_noOffsets(self):
        """
        If the output has no offset lines, an exception is raised.
        """
        text = ("Group           Topic                          Pid "
                "Offset          logSize         Lag             Owner\n")
        self.assertRaises(KafkaNoTopicError, parseOffsets, text)


    def test_noNode(self):
        """
        A failure result raises an exception.
        """
        text = ("Exiting due to: "
                "org.apache.zookeeper.KeeperException$NoNodeException: "
                "KeeperErrorCode = NoNode for "
                "/consumers/group1/offsets/events/11.\n""")
        self.assertRaises(KafkaError, parseOffsets, text)



class KafkaGraphiteServiceTest(unittest.TestCase):

    def setUp(self):
        self.collector = KafkaGraphiteService(
            command="/opt/kafka/bin/kafka-consumer-offset-checker.sh",
            zookeeper="localhost",
            group="group1",
            topic="events")
        self.collector.protocol = FakeGraphiteProtocol()
        self.offsets = {
            0: {'lag': 22,
                'logSize': 734982587,
                'offset': 734982565,
                'owner': 'group1_consumer.example.org-1436585515700-8c4fbc41-0',
            },
            1: {'lag': 23,
                'logSize': 824687314,
                'offset': 824687291,
                'owner': 'group1_consumer.example.org-1436585515700-8c4fbc41-0',
                },
            2: {'lag': None,
                'logSize': 551840689,
                'offset': None,
                'owner': 'group1_consumer.example.org-1436596330605-29002ae5-0',
                }
            }


    def test_gotOffsets(self):
        self.collector.gotOffsets(self.offsets, 'prefix')
        result = self.collector.protocol.output
        self.assertEqual(22.0,
                         result['prefix.0.lag'][0])


    def test_gotUnknownLag(self):
        self.collector.gotOffsets(self.offsets, 'prefix')
        result = self.collector.protocol.output
        self.assertNotIn('prefix.2.lag', result)
