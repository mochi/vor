"""
Service for pulling Kafka stats.
"""

from __future__ import absolute_import

import time
from twisted.application import service
from twisted.internet import task, utils
from twisted.python import log

from vor.graphite import sanitizeMetricElement

class KafkaError(Exception):
    """
    Base for Kafka exceptions.
    """


class KafkaNoTopicError(KafkaError):
    """
    There is no such topic.
    """



def parseOffsets(text):
    """
    Parse ConsumerOffsetChecker output.
    """
    lines = text.split('\n')

    if len(lines) == 2 and not lines[1]:
        line = lines[0]
        if line.startswith('Exiting due to: '):
            raise KafkaError(line[16:])
        else:
            raise KafkaNoTopicError

    offsets = {}
    for line in lines[1:-1]:
        group, topic, pid, offset, logSize, lag, owner = line.split()

        offset = int(offset)
        if offset < 0:
            offset = None

        if lag == 'unknown':
            lag = None
        else:
            lag = int(lag)

        if owner == 'none':
            owner = None

        offsets[int(pid)] = {'offset': offset,
                             'logSize': int(logSize),
                             'lag': lag,
                             'owner': owner}
    return offsets



class KafkaGraphiteService(service.Service):
    """
    Kafka consumer offset poller service.
    """

    def __init__(self, command, zookeeper, group, topic):
        self.command = command
        self.args = ["--zookeeper",
                     zookeeper,
                     "--group",
                     group,
                     "--topic",
                     topic
                     ]

        self.basePath = "kafka.consumer.{topic}.{group}".format(
            topic=sanitizeMetricElement(topic),
            group=sanitizeMetricElement(group))
        self.lc = task.LoopingCall(self.poll)
        self.protocol = None


    def startService(self):
        """
        Start polling Kafka consumer offsets.
        """
        self.lc.start(10)


    def sendMetric(self, path, value, timestamp):
        if self.protocol:
            self.protocol.sendMetric(path, float(value), timestamp)


    def gotOffsets(self, offsets, prefix):
        timestamp = time.time()
        for pid, offset in offsets.iteritems():
            for name in ('offset', 'logSize', 'lag'):
                if offset[name] is None:
                    continue

                path = "{prefix}.{pid}.{name}".format(
                    prefix=prefix,
                    pid=pid,
                    name=name)
                self.sendMetric(path, offset[name], timestamp)


    def poll(self):
        d = utils.getProcessOutput(self.command, self.args)
        d.addCallback(parseOffsets)
        d.addCallback(self.gotOffsets, self.basePath)
        d.addErrback(log.err)
        return d
