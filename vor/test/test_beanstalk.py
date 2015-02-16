"""
Tests for L{vor.beanstalk}.
"""

import time

from twisted.internet import reactor
from twisted.trial import unittest

from vor.graphite import FakeGraphiteProtocol
from vor.beanstalk import BeanstalkGraphiteService

class BeanstalkGraphiteServiceTest(unittest.TestCase):

    def setUp(self):
        self.collector = BeanstalkGraphiteService(reactor, 'localhost', 11300)
        self.collector.protocol = FakeGraphiteProtocol()

        self.stats = {
            'data': {
                'binlog-current-index': 38251,
                'binlog-max-size': 10485760,
                'binlog-oldest-index': 37838,
                'binlog-records-migrated': 50794314,
                'binlog-records-written': 1319757004,
                'cmd-bury': 0,
                'cmd-delete': 363640185,
                'cmd-ignore': 0,
                'cmd-kick': 0,
                'cmd-list-tube-used': 0,
                'cmd-list-tubes': 9,
                'cmd-list-tubes-watched': 0,
                'cmd-pause-tube': 0,
                'cmd-peek': 7482443,
                'cmd-peek-buried': 0,
                'cmd-peek-delayed': 0,
                'cmd-peek-ready': 0,
                'cmd-put': 363619059,
                'cmd-release': 541720773,
                'cmd-reserve': 0,
                'cmd-reserve-with-timeout': 1428990806,
                'cmd-stats': 796,
                'cmd-stats-job': 3263658965,
                'cmd-stats-tube': 4348,
                'cmd-touch': 0,
                'cmd-use': 343686629,
                'cmd-watch': 13871,
                'current-connections': 518,
                'current-jobs-buried': 0,
                'current-jobs-delayed': 4439,
                'current-jobs-ready': 108,
                'current-jobs-reserved': 33,
                'current-jobs-urgent': 0,
                'current-producers': 171,
                'current-tubes': 17,
                'current-waiting': 312,
                'current-workers': 345,
                'job-timeouts': 1959,
                'max-job-size': 65535,
                'pid': 974,
                'rusage-stime': 215212.02191,
                'rusage-utime': 98421.882983,
                'total-connections': 22336794,
                'total-jobs': 363619059,
                'uptime': 9296864,
                'version': 1.5
                },
            'state': 'ok',
            'bytes': 991
            }


    def test_gotStats(self):
        """
        Stats metrics are emitted as metrics.
        """
        self.collector.gotStats(self.stats, 'prefix')
        result = self.collector.protocol.output
        self.assertEqual(
                17,
                result['prefix.current-tubes'][0])


    def test_gotStatsTimestamp(self):
        """
        Stats metrics have a timestamp.
        """
        self.collector.gotStats(self.stats, 'prefix')
        result = self.collector.protocol.output
        self.assertApproximates(
                time.time(),
                result['prefix.current-tubes'][1],
                3)


    def test_gotStatsNoVersion(self):
        """
        Stats metrics have no version metric.
        """
        self.collector.gotStats(self.stats, 'prefix')
        result = self.collector.protocol.output
        self.assertNotIn('prefix.version', result)


    def test_gotStatsNoPID(self):
        """
        Stats metrics have not PID metric.
        """
        self.collector.gotStats(self.stats, 'prefix')
        result = self.collector.protocol.output
        self.assertNotIn('prefix.pid', result)
