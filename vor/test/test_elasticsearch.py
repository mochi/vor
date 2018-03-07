import json
import time

from twisted.trial import unittest

from vor.graphite import FakeGraphiteProtocol
from vor.elasticsearch import ElasticSearchStatsGraphiteService
from vor.elasticsearch import ElasticSearchNodeStatsGraphiteService
from vor.elasticsearch import ElasticSearchHealthGraphiteService

class ElasticSearchStatsGraphiteServiceTest(unittest.TestCase):
    """
    Tests for L{ElasticSearchStatsGraphiteService}.
    """

    def setUp(self):
        self.collector = ElasticSearchStatsGraphiteService(
            'http://localhost:9200/')
        self.collector.protocol = FakeGraphiteProtocol()
        stats = """
{
    "timestamp": 1391786444651,
    "cluster_name": "mailgun",
    "status": "yellow",
    "indices": {
        "count": 63,
        "shards": {
            "total": 363,
            "primaries": 315,
            "replication": 0.1523809523809524,
            "index": {
                "shards": {
                    "min": 5,
                    "max": 10,
                    "avg": 5.761904761904762
                },
                "primaries": {
                    "min": 5,
                    "max": 5,
                    "avg": 5
                },
                "replication": {
                    "min": 0,
                    "max": 1,
                    "avg": 0.15238095238095237
                }
            }
        },
        "docs": {
            "count": 2953827122,
            "deleted": 2
        },
        "store": {
            "size": "4.9tb",
            "size_in_bytes": 5392713706486,
            "throttle_time": "2.3h",
            "throttle_time_in_millis": 8498728
        },
        "fielddata": {
            "memory_size": "8.1gb",
            "memory_size_in_bytes": 8785071710,
            "evictions": 0
        },
        "filter_cache": {
            "memory_size": "38.2gb",
            "memory_size_in_bytes": 41028183795,
            "evictions": 3077519
        },
        "id_cache": {
            "memory_size": "0b",
            "memory_size_in_bytes": 0
        },
        "completion": {
            "size": "0b",
            "size_in_bytes": 0
        },
        "segments": {
            "count": 9680,
            "memory": "41.1gb",
            "memory_in_bytes": 44137105565
        }
    },
    "nodes": {
        "count": {
            "total": 9,
            "master_only": 0,
            "data_only": 0,
            "master_data": 6,
            "client": 0
        },
        "versions": [
            "0.90.11"
        ],
        "os": {
            "available_processors": 152,
            "mem": {
                "total": "392.8gb",
                "total_in_bytes": 421821104128
            },
            "cpu": [
                {
                    "vendor": "AMD",
                    "model": "Opteron",
                    "mhz": 3000,
                    "total_cores": 4,
                    "total_sockets": 4,
                    "cores_per_socket": 6,
                    "cache_size": "2kb",
                    "cache_size_in_bytes": 2048,
                    "count": 3
                },
                {
                    "vendor": "Intel",
                    "model": "Xeon",
                    "mhz": 2501,
                    "total_cores": 24,
                    "total_sockets": 24,
                    "cores_per_socket": 32,
                    "cache_size": "15kb",
                    "cache_size_in_bytes": 15360,
                    "count": 6
                }
            ]
        },
        "process": {
            "cpu": {
                "percent": 1429
            },
            "open_file_descriptors": {
                "min": 349,
                "max": 11060,
                "avg": 6170
            }
        },
        "jvm": {
            "max_uptime": "1.5h",
            "max_uptime_in_millis": 5753523,
            "versions": [
                {
                    "version": "1.7.0_51",
                    "vm_name": "OpenJDK 64-Bit Server VM",
                    "vm_version": "24.45-b08",
                    "vm_vendor": "Oracle Corporation",
                    "count": 6
                },
                {
                    "version": "1.7.0_21",
                    "vm_name": "OpenJDK 64-Bit Server VM",
                    "vm_version": "23.7-b01",
                    "vm_vendor": "Oracle Corporation",
                    "count": 3
                }
            ],
            "mem": {
                "heap_used": "112.3gb",
                "heap_used_in_bytes": 120615407032,
                "heap_max": "197.7gb",
                "heap_max_in_bytes": 212331397120
            },
            "threads": 1845
        },
        "fs": {
            "total": "12.8tb",
            "total_in_bytes": 14163419111424,
            "free": "4.2tb",
            "free_in_bytes": 4667468734464,
            "available": "3.5tb",
            "available_in_bytes": 3948008669184,
            "disk_reads": 1652262147,
            "disk_writes": 1584903467,
            "disk_io_op": 3237165614,
            "disk_read_size": "83.7tb",
            "disk_read_size_in_bytes": 92098248648704,
            "disk_write_size": "237.8tb",
            "disk_write_size_in_bytes": 261555186733056,
            "disk_io_size": "321.6tb",
            "disk_io_size_in_bytes": 353653435381760,
            "disk_queue": "0",
            "disk_service_time": "12.8"
        },
        "plugins": [
            {
                "name": "bigdesk",
                "description": "No description found for bigdesk.",
                "url": "/_plugin/bigdesk/",
                "jvm": false,
                "site": true
            },
            {
                "name": "head",
                "description": "No description found for head.",
                "url": "/_plugin/head/",
                "jvm": false,
                "site": true
            },
            {
                "name": "paramedic",
                "description": "No description found for paramedic.",
                "url": "/_plugin/paramedic/",
                "jvm": false,
                "site": true
            }
        ]
    }

}"""

        data = json.loads(stats)
        self.collector.flatten(data)
        self.result = self.collector.protocol.output



    def test_timestamp(self):
        """
        Metrics have a timestamp.
        """
        self.assertEquals(1391786444.651,
                          self.result['es.cluster.indices.count'][1])

    def test_noCpuStats(self):
        """
        Mostly static CPU stats are not included in timeseries.
        """
        self.assertNotIn('es.cluster.nodes.os.cpu.0.cache_size', self.result)



class ElasticSearchNodeStatsGraphiteServiceTest(unittest.TestCase):

    def setUp(self):
        self.collector = ElasticSearchNodeStatsGraphiteService(
            'http://localhost:9200/')
        self.collector.protocol = FakeGraphiteProtocol()
        self.collector_hostname_only = ElasticSearchNodeStatsGraphiteService(
            'http://localhost:9200/', hostname_only=True)
        self.collector_hostname_only.protocol = FakeGraphiteProtocol()
        stats = """
{
    "nodes" : {
        "ByaOeCBdQoCZxMBcRI__Zw" : {
            "transport" : {
                "tx_size_in_bytes" : 27883456150,
                "tx_count" : 31763326,
                "rx_size" : "18.4gb",
                "server_open" : 18,
                "rx_size_in_bytes" : 19821307301,
                "rx_count" : 37576602,
                "tx_size" : "25.9gb"
            },
            "network" : {},
            "name" : "graylog2",
            "hostname" : "es-proxy.example.org",
            "process" : {
                "open_file_descriptors" : 183,
                "timestamp" : 1354643578330
            },
            "os" : {
                "timestamp" : 1354643578330
            },
            "transport_address" : "inet[/127.0.0.1:9350]",
            "thread_pool" : {
                "search" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "bulk" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "generic" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 1
                },
                "index" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "refresh" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "merge" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "flush" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "percolate" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "get" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "snapshot" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "management" : {
                    "active" : 1,
                    "queue" : 0,
                    "threads" : 1
                },
                "cache" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                }
            },
            "timestamp" : 1354643578330,
            "indices" : {
                "indexing" : {
                    "delete_total" : 0,
                    "delete_current" : 0,
                    "index_current" : 0,
                    "index_total" : 0,
                    "index_time" : "0s",
                    "delete_time" : "0s",
                    "delete_time_in_millis" : 0,
                    "index_time_in_millis" : 0
                },
                "search" : {
                    "query_time_in_millis" : 0,
                    "fetch_time" : "0s",
                    "fetch_total" : 0,
                    "fetch_current" : 0,
                    "query_current" : 0,
                    "query_time" : "0s",
                    "query_total" : 0,
                    "fetch_time_in_millis" : 0
                },
                "store" : {
                    "throttle_time" : "0s",
                    "size_in_bytes" : 0,
                    "throttle_time_in_millis" : 0,
                    "size" : "0b"
                },
                "flush" : {
                    "total_time_in_millis" : 0,
                    "total_time" : "0s",
                    "total" : 0
                },
                "refresh" : {
                    "total_time_in_millis" : 0,
                    "total_time" : "0s",
                    "total" : 0
                },
                "get" : {
                    "missing_total" : 0,
                    "time" : "0s",
                    "time_in_millis" : 0,
                    "exists_total" : 0,
                    "total" : 0,
                    "exists_time" : "0s",
                    "current" : 0,
                    "missing_time" : "0s",
                    "missing_time_in_millis" : 0,
                    "exists_time_in_millis" : 0
                },
                "merges" : {
                    "total_docs" : 0,
                    "total_size_in_bytes" : 0,
                    "current_docs" : 0,
                    "total_size" : "0b",
                    "total" : 0,
                    "current_size" : "0b",
                    "current_size_in_bytes" : 0,
                    "current" : 0,
                    "total_time_in_millis" : 0,
                    "total_time" : "0s"
                },
                "docs" : {
                    "count" : 0,
                    "deleted" : 0
                },
                "cache" : {
                    "filter_size" : "0b",
                    "field_evictions" : 0,
                    "field_size_in_bytes" : 0,
                    "filter_size_in_bytes" : 0,
                    "filter_evictions" : 0,
                    "field_size" : "0b",
                    "filter_count" : 0
                }
            },
            "fs" : {
                "timestamp" : 1354643578330,
                "data" : []
            },
            "jvm" : {
                "timestamp" : 1354643578330,
                "uptime_in_millis" : 21379254,
                "uptime" : "5 hours, 56 minutes, 19 seconds and 254 milliseconds",
                "gc" : {
                    "collection_time_in_millis" : 225164,
                    "collectors" : {
                        "PS MarkSweep" : {
                            "collection_time_in_millis" : 81722,
                            "collection_time" : "1 minute, 21 seconds and 722 milliseconds",
                            "collection_count" : 39
                        },
                        "PS Scavenge" : {
                            "collection_time_in_millis" : 143442,
                            "collection_time" : "2 minutes, 23 seconds and 442 milliseconds",
                            "collection_count" : 2281
                        }
                    },
                    "collection_time" : "3 minutes, 45 seconds and 164 milliseconds",
                    "collection_count" : 2320
                },
                "mem" : {
                    "heap_used" : "4.2gb",
                    "non_heap_used_in_bytes" : 43032632,
                    "heap_committed_in_bytes" : 7929069568,
                    "heap_used_in_bytes" : 4566020208,
                    "heap_committed" : "7.3gb",
                    "non_heap_used" : "41mb",
                    "non_heap_committed_in_bytes" : 43515904,
                    "non_heap_committed" : "41.5mb",
                    "pools" : {
                        "PS Survivor Space" : {
                            "peak_max" : "773.3mb",
                            "peak_max_in_bytes" : 810876928,
                            "peak_used" : "548.1mb",
                            "max_in_bytes" : 73138176,
                            "max" : "69.7mb",
                            "used" : "58mb",
                            "used_in_bytes" : 60817408,
                            "peak_used_in_bytes" : 574746912
                        },
                        "Code Cache" : {
                            "peak_max" : "48mb",
                            "peak_max_in_bytes" : 50331648,
                            "peak_used" : "6.2mb",
                            "max_in_bytes" : 50331648,
                            "max" : "48mb",
                            "used" : "6.1mb",
                            "used_in_bytes" : 6498688,
                            "peak_used_in_bytes" : 6549696
                        },
                        "PS Eden Space" : {
                            "peak_max" : "2.5gb",
                            "peak_max_in_bytes" : 2762866688,
                            "peak_used" : "2.4gb",
                            "max_in_bytes" : 2659385344,
                            "max" : "2.4gb",
                            "used" : "1.6gb",
                            "used_in_bytes" : 1757215688,
                            "peak_used_in_bytes" : 2659581952
                        },
                        "PS Perm Gen" : {
                            "peak_max" : "84mb",
                            "peak_max_in_bytes" : 88080384,
                            "peak_used" : "34.8mb",
                            "max_in_bytes" : 88080384,
                            "max" : "84mb",
                            "used" : "34.8mb",
                            "used_in_bytes" : 36533944,
                            "peak_used_in_bytes" : 36540152
                        },
                        "PS Old Gen" : {
                            "peak_max" : "5.2gb",
                            "peak_max_in_bytes" : 5613420544,
                            "peak_used" : "5.2gb",
                            "max_in_bytes" : 5613420544,
                            "max" : "5.2gb",
                            "used" : "2.5gb",
                            "used_in_bytes" : 2747987112,
                            "peak_used_in_bytes" : 5607837424
                        }
                    }
                },
                "threads" : {
                    "count" : 89,
                    "peak_count" : 92
                }
            },
            "attributes" : {
                "client" : "true",
                "master" : "false",
                "data" : "false"
            }
        },
        "6S1L32BGQjutA8AfFIrzLQ" : {
            "transport" : {
                "tx_size_in_bytes" : 34571056,
                "tx_count" : 411460,
                "rx_size" : "7.2gb",
                "server_open" : 36,
                "rx_size_in_bytes" : 7801719352,
                "rx_count" : 642642,
                "tx_size" : "32.9mb"
            },
            "network" : {
                "tcp" : {
                    "attempt_fails" : 9758,
                    "active_opens" : 541922,
                    "in_errs" : 0,
                    "in_segs" : 3597472088,
                    "out_rsts" : 11797,
                    "curr_estab" : 319,
                    "retrans_segs" : 525889,
                    "out_segs" : 3374986054,
                    "estab_resets" : 1597,
                    "passive_opens" : 496338
                }
            },
            "name" : "es-proxy",
            "hostname" : "es-proxy.example.org",
            "process" : {
                "cpu" : {
                    "user_in_millis" : 2081010,
                    "sys_in_millis" : 159650,
                    "sys" : "2 minutes, 39 seconds and 650 milliseconds",
                    "percent" : 2,
                    "user" : "34 minutes, 41 seconds and 10 milliseconds",
                    "total" : "37 minutes, 20 seconds and 660 milliseconds",
                    "total_in_millis" : 2240660
                },
                "open_file_descriptors" : 534,
                "timestamp" : 1354643578331,
                "mem" : {
                    "share" : "10.6mb",
                    "total_virtual" : "6.2gb",
                    "share_in_bytes" : 11202560,
                    "resident_in_bytes" : 5554737152,
                    "total_virtual_in_bytes" : 6688526336,
                    "resident" : "5.1gb"
                }
            },
            "os" : {
                "load_average" : [
                    10.48,
                    10.46,
                    10.39
                ],
                "cpu" : {
                    "sys" : 8,
                    "user" : 25,
                    "idle" : 65
                },
                "timestamp" : 1354643578330,
                "swap" : {
                    "free" : "0b",
                    "used" : "0b",
                    "used_in_bytes" : 0,
                    "free_in_bytes" : 0
                },
                "uptime_in_millis" : 1532672000,
                "uptime" : "425 hours, 44 minutes and 32 seconds",
                "mem" : {
                    "actual_used" : "18.6gb",
                    "actual_used_in_bytes" : 20058361856,
                    "free_percent" : 40,
                    "actual_free" : "12.6gb",
                    "free" : "9.2gb",
                    "actual_free_in_bytes" : 13613740032,
                    "used" : "22.1gb",
                    "used_in_bytes" : 23738146816,
                    "used_percent" : 59,
                    "free_in_bytes" : 9933955072
                }
            },
            "transport_address" : "inet[/127.0.0.1:9300]",
            "thread_pool" : {
                "search" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "bulk" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "generic" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 1
                },
                "index" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "refresh" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "merge" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "flush" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "percolate" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "get" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "snapshot" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "management" : {
                    "active" : 1,
                    "queue" : 0,
                    "threads" : 1
                },
                "cache" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                }
            },
            "http" : {
                "current_open" : 0,
                "total_opened" : 51
            },
            "timestamp" : 1354643578330,
            "indices" : {
                "indexing" : {
                    "delete_total" : 0,
                    "delete_current" : 0,
                    "index_current" : 0,
                    "index_total" : 0,
                    "index_time" : "0s",
                    "delete_time" : "0s",
                    "delete_time_in_millis" : 0,
                    "index_time_in_millis" : 0
                },
                "search" : {
                    "query_time_in_millis" : 0,
                    "fetch_time" : "0s",
                    "fetch_total" : 0,
                    "fetch_current" : 0,
                    "query_current" : 0,
                    "query_time" : "0s",
                    "query_total" : 0,
                    "fetch_time_in_millis" : 0
                },
                "store" : {
                    "throttle_time" : "0s",
                    "size_in_bytes" : 0,
                    "throttle_time_in_millis" : 0,
                    "size" : "0b"
                },
                "flush" : {
                    "total_time_in_millis" : 0,
                    "total_time" : "0s",
                    "total" : 0
                },
                "refresh" : {
                    "total_time_in_millis" : 0,
                    "total_time" : "0s",
                    "total" : 0
                },
                "get" : {
                    "missing_total" : 0,
                    "time" : "0s",
                    "time_in_millis" : 0,
                    "exists_total" : 0,
                    "total" : 0,
                    "exists_time" : "0s",
                    "current" : 0,
                    "missing_time" : "0s",
                    "missing_time_in_millis" : 0,
                    "exists_time_in_millis" : 0
                },
                "merges" : {
                    "total_docs" : 0,
                    "total_size_in_bytes" : 0,
                    "current_docs" : 0,
                    "total_size" : "0b",
                    "total" : 0,
                    "current_size" : "0b",
                    "current_size_in_bytes" : 0,
                    "current" : 0,
                    "total_time_in_millis" : 0,
                    "total_time" : "0s"
                },
                "docs" : {
                    "count" : 0,
                    "deleted" : 0
                },
                "cache" : {
                    "filter_size" : "0b",
                    "field_evictions" : 0,
                    "field_size_in_bytes" : 0,
                    "filter_size_in_bytes" : 0,
                    "filter_evictions" : 0,
                    "field_size" : "0b",
                    "filter_count" : 0
                }
            },
            "fs" : {
                "timestamp" : 1354643578333,
                "data" : [
                    {
                        "disk_read_size" : "980.4mb",
                        "free" : "408.5gb",
                        "free_in_bytes" : 438690443264,
                        "available" : "408.5gb",
                        "disk_reads" : 239762,
                        "dev" : "/dev/sda3",
                        "mount" : "/data",
                        "total_in_bytes" : 440468504576,
                        "path" : "/data/elasticsearch/production/nodes/0",
                        "disk_read_size_in_bytes" : 1028058624,
                        "disk_service_time" : "0.6",
                        "total" : "410.2gb",
                        "available_in_bytes" : 438690443264,
                        "disk_queue" : "0.3",
                        "disk_writes" : 5065376,
                        "disk_write_size_in_bytes" : 53740348416,
                        "disk_write_size" : "50gb"
                    }
                ]
            },
            "jvm" : {
                "timestamp" : 1354643578331,
                "uptime_in_millis" : 23435527,
                "uptime" : "6 hours, 30 minutes, 35 seconds and 527 milliseconds",
                "gc" : {
                    "collection_time_in_millis" : 40284,
                    "collectors" : {
                        "ParNew" : {
                            "collection_time_in_millis" : 39826,
                            "collection_time" : "39 seconds and 826 milliseconds",
                            "collection_count" : 604
                        },
                        "ConcurrentMarkSweep" : {
                            "collection_time_in_millis" : 458,
                            "collection_time" : "458 milliseconds",
                            "collection_count" : 2
                        }
                    },
                    "collection_time" : "40 seconds and 284 milliseconds",
                    "collection_count" : 606
                },
                "mem" : {
                    "heap_used" : "2gb",
                    "non_heap_used_in_bytes" : 42645936,
                    "heap_committed_in_bytes" : 4255711232,
                    "heap_used_in_bytes" : 2210496040,
                    "heap_committed" : "3.9gb",
                    "non_heap_used" : "40.6mb",
                    "non_heap_committed_in_bytes" : 68362240,
                    "non_heap_committed" : "65.1mb",
                    "pools" : {
                        "Code Cache" : {
                            "peak_max" : "48mb",
                            "peak_max_in_bytes" : 50331648,
                            "peak_used" : "3.8mb",
                            "max_in_bytes" : 50331648,
                            "max" : "48mb",
                            "used" : "3.8mb",
                            "used_in_bytes" : 4080704,
                            "peak_used_in_bytes" : 4083392
                        },
                        "Par Survivor Space" : {
                            "peak_max" : "37.4mb",
                            "peak_max_in_bytes" : 39256064,
                            "peak_used" : "37.4mb",
                            "max_in_bytes" : 39256064,
                            "max" : "37.4mb",
                            "used" : "4.3mb",
                            "used_in_bytes" : 4599552,
                            "peak_used_in_bytes" : 39256064
                        },
                        "CMS Old Gen" : {
                            "peak_max" : "3.6gb",
                            "peak_max_in_bytes" : 3902406656,
                            "peak_used" : "2.7gb",
                            "max_in_bytes" : 3902406656,
                            "max" : "3.6gb",
                            "used" : "2gb",
                            "used_in_bytes" : 2162732576,
                            "peak_used_in_bytes" : 2952485360
                        },
                        "CMS Perm Gen" : {
                            "peak_max" : "84mb",
                            "peak_max_in_bytes" : 88080384,
                            "peak_used" : "36.7mb",
                            "max_in_bytes" : 88080384,
                            "max" : "84mb",
                            "used" : "36.7mb",
                            "used_in_bytes" : 38565232,
                            "peak_used_in_bytes" : 38565232
                        },
                        "Par Eden Space" : {
                            "peak_max" : "299.5mb",
                            "peak_max_in_bytes" : 314048512,
                            "peak_used" : "299.5mb",
                            "max_in_bytes" : 314048512,
                            "max" : "299.5mb",
                            "used" : "41.1mb",
                            "used_in_bytes" : 43163912,
                            "peak_used_in_bytes" : 314048512
                        }
                    }
                },
                "threads" : {
                    "count" : 159,
                    "peak_count" : 161
                }
            },
            "attributes" : {
                "river" : "_none_",
                "master" : "true",
                "data" : "false"
            }
        },
        "lLiEdHWZQIKTpAz5jZL97g" : {
            "transport" : {
                "tx_size_in_bytes" : 636120364,
                "tx_count" : 467453,
                "rx_size" : "47.3mb",
                "server_open" : 18,
                "rx_size_in_bytes" : 49647180,
                "rx_count" : 468089,
                "tx_size" : "606.6mb"
            },
            "network" : {},
            "name" : "logstash",
            "hostname" : "es-proxy.example.org",
            "process" : {
                "open_file_descriptors" : 351,
                "timestamp" : 1354643578336
            },
            "os" : {
                "timestamp" : 1354643578336
            },
            "transport_address" : "inet[/127.0.0.1:9301]",
            "thread_pool" : {
                "search" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "bulk" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "generic" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 1
                },
                "index" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "refresh" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "merge" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "flush" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "percolate" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "get" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "snapshot" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "management" : {
                    "active" : 1,
                    "queue" : 0,
                    "threads" : 1
                },
                "cache" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                }
            },
            "timestamp" : 1354643578333,
            "indices" : {
                "indexing" : {
                    "delete_total" : 0,
                    "delete_current" : 0,
                    "index_current" : 0,
                    "index_total" : 0,
                    "index_time" : "0s",
                    "delete_time" : "0s",
                    "delete_time_in_millis" : 0,
                    "index_time_in_millis" : 0
                },
                "search" : {
                    "query_time_in_millis" : 0,
                    "fetch_time" : "0s",
                    "fetch_total" : 0,
                    "fetch_current" : 0,
                    "query_current" : 0,
                    "query_time" : "0s",
                    "query_total" : 0,
                    "fetch_time_in_millis" : 0
                },
                "store" : {
                    "throttle_time" : "0s",
                    "size_in_bytes" : 0,
                    "throttle_time_in_millis" : 0,
                    "size" : "0b"
                },
                "flush" : {
                    "total_time_in_millis" : 0,
                    "total_time" : "0s",
                    "total" : 0
                },
                "refresh" : {
                    "total_time_in_millis" : 0,
                    "total_time" : "0s",
                    "total" : 0
                },
                "get" : {
                    "missing_total" : 0,
                    "time" : "0s",
                    "time_in_millis" : 0,
                    "exists_total" : 0,
                    "total" : 0,
                    "exists_time" : "0s",
                    "current" : 0,
                    "missing_time" : "0s",
                    "missing_time_in_millis" : 0,
                    "exists_time_in_millis" : 0
                },
                "merges" : {
                    "total_docs" : 0,
                    "total_size_in_bytes" : 0,
                    "current_docs" : 0,
                    "total_size" : "0b",
                    "total" : 0,
                    "current_size" : "0b",
                    "current_size_in_bytes" : 0,
                    "current" : 0,
                    "total_time_in_millis" : 0,
                    "total_time" : "0s"
                },
                "docs" : {
                    "count" : 0,
                    "deleted" : 0
                },
                "cache" : {
                    "filter_size" : "0b",
                    "field_evictions" : 0,
                    "field_size_in_bytes" : 0,
                    "filter_size_in_bytes" : 0,
                    "filter_evictions" : 0,
                    "field_size" : "0b",
                    "filter_count" : 0
                }
            },
            "fs" : {
                "timestamp" : 1354643578337,
                "data" : []
            },
            "jvm" : {
                "timestamp" : 1354643578336,
                "uptime_in_millis" : 456758,
                "uptime" : "7 minutes, 36 seconds and 758 milliseconds",
                "gc" : {
                    "collection_time_in_millis" : 3801,
                    "collectors" : {
                        "PS MarkSweep" : {
                            "collection_time_in_millis" : 0,
                            "collection_time" : "0 milliseconds",
                            "collection_count" : 0
                        },
                        "PS Scavenge" : {
                            "collection_time_in_millis" : 3801,
                            "collection_time" : "3 seconds and 801 milliseconds",
                            "collection_count" : 301
                        }
                    },
                    "collection_time" : "3 seconds and 801 milliseconds",
                    "collection_count" : 301
                },
                "mem" : {
                    "heap_used" : "2.1gb",
                    "non_heap_used_in_bytes" : 71231672,
                    "heap_committed_in_bytes" : 3024748544,
                    "heap_used_in_bytes" : 2336625824,
                    "heap_committed" : "2.8gb",
                    "non_heap_used" : "67.9mb",
                    "non_heap_committed_in_bytes" : 71565312,
                    "non_heap_committed" : "68.2mb",
                    "pools" : {
                        "PS Survivor Space" : {
                            "peak_max" : "20.8mb",
                            "peak_max_in_bytes" : 21889024,
                            "peak_used" : "10.5mb",
                            "max_in_bytes" : 6160384,
                            "max" : "5.8mb",
                            "used" : "4.8mb",
                            "used_in_bytes" : 5046272,
                            "peak_used_in_bytes" : 11022824
                        },
                        "Code Cache" : {
                            "peak_max" : "48mb",
                            "peak_max_in_bytes" : 50331648,
                            "peak_used" : "11.4mb",
                            "max_in_bytes" : 50331648,
                            "max" : "48mb",
                            "used" : "11.4mb",
                            "used_in_bytes" : 11987136,
                            "peak_used_in_bytes" : 11998272
                        },
                        "PS Eden Space" : {
                            "peak_max" : "2.6gb",
                            "peak_max_in_bytes" : 2803826688,
                            "peak_used" : "2.6gb",
                            "max_in_bytes" : 2793865216,
                            "max" : "2.6gb",
                            "used" : "2gb",
                            "used_in_bytes" : 2196701496,
                            "peak_used_in_bytes" : 2794061824
                        },
                        "PS Perm Gen" : {
                            "peak_max" : "84mb",
                            "peak_max_in_bytes" : 88080384,
                            "peak_used" : "56.4mb",
                            "max_in_bytes" : 88080384,
                            "max" : "84mb",
                            "used" : "56.4mb",
                            "used_in_bytes" : 59244536,
                            "peak_used_in_bytes" : 59244536
                        },
                        "PS Old Gen" : {
                            "peak_max" : "5.2gb",
                            "peak_max_in_bytes" : 5613420544,
                            "peak_used" : "128.6mb",
                            "max_in_bytes" : 5613420544,
                            "max" : "5.2gb",
                            "used" : "128.6mb",
                            "used_in_bytes" : 134878056,
                            "peak_used_in_bytes" : 134878056
                        }
                    }
                },
                "threads" : {
                    "count" : 124,
                    "peak_count" : 125
                }
            },
            "attributes" : {
                "client" : "true",
                "data" : "false"
            }
        },
        "-WvxxOCwRxiZNLfDJ01wWg" : {
            "attributes" : {
            },
            "transport" : {
                "tx_size_in_bytes" : 110660992351,
                "tx_count" : 191366777,
                "rx_size" : "194.6gb",
                "server_open" : 36,
                "rx_size_in_bytes" : 208983333503,
                "rx_count" : 215563463,
                "tx_size" : "103gb"
            },
            "network" : {
                "tcp" : {
                    "attempt_fails" : 29763,
                    "active_opens" : 838369,
                    "in_errs" : 1,
                    "in_segs" : 7899923061,
                    "out_rsts" : 35788,
                    "curr_estab" : 189,
                    "retrans_segs" : 49103,
                    "out_segs" : 5958564488,
                    "estab_resets" : 74994,
                    "passive_opens" : 288379
                }
            },
            "name" : "es-data.example.org",
            "hostname" : "es-data.example.org",
            "process" : {
                "cpu" : {
                    "user_in_millis" : 446942840,
                    "sys_in_millis" : 30208150,
                    "sys" : "8 hours, 23 minutes, 28 seconds and 150 milliseconds",
                    "percent" : 666,
                    "user" : "124 hours, 9 minutes, 2 seconds and 840 milliseconds",
                    "total" : "132 hours, 32 minutes, 30 seconds and 990 milliseconds",
                    "total_in_millis" : 477150990
                },
                "open_file_descriptors" : 51334,
                "timestamp" : 1354643578355,
                "mem" : {
                    "share" : "16.6mb",
                    "total_virtual" : "25.3gb",
                    "share_in_bytes" : 17428480,
                    "resident_in_bytes" : 26850566144,
                    "total_virtual_in_bytes" : 27237588992,
                    "resident" : "25gb"
                }
            },
            "os" : {
                "load_average" : [
                    8.15,
                    10.78,
                    11.92
                ],
                "cpu" : {
                    "sys" : 1,
                    "user" : 26,
                    "idle" : 60
                },
                "timestamp" : 1354643578355,
                "swap" : {
                    "free" : "0b",
                    "used" : "0b",
                    "used_in_bytes" : 0,
                    "free_in_bytes" : 0
                },
                "uptime_in_millis" : 6985885000,
                "uptime" : "1940 hours, 31 minutes and 25 seconds",
                "mem" : {
                    "actual_used" : "25.6gb",
                    "actual_used_in_bytes" : 27570733056,
                    "free_percent" : 18,
                    "actual_free" : "5.6gb",
                    "free" : "90.2mb",
                    "actual_free_in_bytes" : 6101368832,
                    "used" : "31.2gb",
                    "used_in_bytes" : 33577492480,
                    "used_percent" : 81,
                    "free_in_bytes" : 94609408
                }
            },
            "transport_address" : "inet[/10.0.8.74:9300]",
            "thread_pool" : {
                "search" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "bulk" : {
                    "rejected" : 0,
                    "active" : 1,
                    "queue" : 0,
                    "threads" : 79
                },
                "generic" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 2
                },
                "index" : {
                    "rejected" : 0,
                    "active" : 2,
                    "queue" : 0,
                    "threads" : 50
                },
                "refresh" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 10
                },
                "flush" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 10
                },
                "merge" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 20
                },
                "percolate" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "get" : {
                    "rejected" : 0,
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 0
                },
                "snapshot" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 5
                },
                "management" : {
                    "active" : 1,
                    "queue" : 0,
                    "threads" : 5
                },
                "cache" : {
                    "active" : 0,
                    "queue" : 0,
                    "threads" : 4
                }
            },
            "http" : {
                "current_open" : 1,
                "total_opened" : 6
            },
            "timestamp" : 1354643578332,
            "indices" : {
                "indexing" : {
                    "delete_total" : 69063858,
                    "delete_current" : 0,
                    "index_current" : 0,
                    "index_total" : 212821207,
                    "index_time" : "6.3d",
                    "delete_time" : "1.3h",
                    "delete_time_in_millis" : 4701247,
                    "index_time_in_millis" : 552239795
                },
                "search" : {
                    "query_time_in_millis" : 28137821,
                    "fetch_time" : "6.1s",
                    "fetch_total" : 619,
                    "fetch_current" : 0,
                    "query_current" : 0,
                    "query_time" : "7.8h",
                    "query_total" : 4120,
                    "fetch_time_in_millis" : 6188
                },
                "store" : {
                    "throttle_time" : "0s",
                    "size_in_bytes" : 1346875050349,
                    "throttle_time_in_millis" : 0,
                    "size" : "1254.3gb"
                },
                "flush" : {
                    "total_time_in_millis" : 64269820,
                    "total_time" : "17.8h",
                    "total" : 81931
                },
                "refresh" : {
                    "total_time_in_millis" : 69045256,
                    "total_time" : "19.1h",
                    "total" : 592732
                },
                "get" : {
                    "missing_total" : 0,
                    "time" : "0s",
                    "time_in_millis" : 0,
                    "exists_total" : 0,
                    "total" : 0,
                    "exists_time" : "0s",
                    "current" : 0,
                    "missing_time" : "0s",
                    "missing_time_in_millis" : 0,
                    "exists_time_in_millis" : 0
                },
                "merges" : {
                    "total_docs" : 185892827,
                    "total_size_in_bytes" : 354709832617,
                    "current_docs" : 395736,
                    "total_size" : "330.3gb",
                    "total" : 13699,
                    "current_size" : "780.2mb",
                    "current_size_in_bytes" : 818199256,
                    "current" : 1,
                    "total_time_in_millis" : 79241907,
                    "total_time" : "22h"
                },
                "docs" : {
                    "count" : 696374222,
                    "deleted" : 740573
                },
                "cache" : {
                    "filter_size" : "71mb",
                    "field_evictions" : 0,
                    "field_size_in_bytes" : 3466624848,
                    "filter_size_in_bytes" : 74508280,
                    "filter_evictions" : 0,
                    "field_size" : "3.2gb",
                    "filter_count" : 46
                }
            },
            "fs" : {
                "timestamp" : 1354643578364,
                "data" : [
                    {
                        "disk_read_size" : "11228.9gb",
                        "free" : "1205.7gb",
                        "free_in_bytes" : 1294692122624,
                        "available" : "1112.6gb",
                        "disk_reads" : 163734630,
                        "dev" : "/dev/sdb1",
                        "mount" : "/data1",
                        "total_in_bytes" : 1968465301504,
                        "path" : "/data1/elasticsearch/production/nodes/0",
                        "disk_read_size_in_bytes" : 12056946306560,
                        "disk_service_time" : "5.7",
                        "total" : "1833.2gb",
                        "available_in_bytes" : 1194699919360,
                        "disk_queue" : "0",
                        "disk_writes" : 540690082,
                        "disk_write_size_in_bytes" : 45577478289408,
                        "disk_write_size" : "42447.3gb"
                    },
                    {
                        "disk_read_size" : "10970gb",
                        "free" : "1205.7gb",
                        "free_in_bytes" : 1294672719872,
                        "available" : "1112.6gb",
                        "disk_reads" : 160809452,
                        "dev" : "/dev/sdc1",
                        "mount" : "/data2",
                        "total_in_bytes" : 1968465301504,
                        "path" : "/data2/elasticsearch/production/nodes/0",
                        "disk_read_size_in_bytes" : 11778948320768,
                        "disk_service_time" : "5.7",
                        "total" : "1833.2gb",
                        "available_in_bytes" : 1194680516608,
                        "disk_queue" : "0",
                        "disk_writes" : 544906136,
                        "disk_write_size_in_bytes" : 44799813470208,
                        "disk_write_size" : "41723gb"
                    }
                ]
            },
            "jvm" : {
                "buffer_pools" : {
                    "direct" : {
                        "total_capacity_in_bytes" : 118752332,
                        "count" : 459,
                        "used" : "113.2mb",
                        "used_in_bytes" : 118752332,
                        "total_capacity" : "113.2mb"
                    },
                    "mapped" : {
                        "total_capacity_in_bytes" : 0,
                        "count" : 0,
                        "used" : "0b",
                        "used_in_bytes" : 0,
                        "total_capacity" : "0b"
                    }
                },
                "timestamp" : 1354643578362,
                "uptime_in_millis" : 109840215,
                "uptime" : "30 hours, 30 minutes, 40 seconds and 215 milliseconds",
                "gc" : {
                    "collection_time_in_millis" : 4343558,
                    "collectors" : {
                        "ParNew" : {
                            "collection_time_in_millis" : 2783256,
                            "collection_time" : "46 minutes, 23 seconds and 256 milliseconds",
                            "collection_count" : 24977
                        },
                        "ConcurrentMarkSweep" : {
                            "collection_time_in_millis" : 1560302,
                            "collection_time" : "26 minutes and 302 milliseconds",
                            "collection_count" : 1603
                        }
                    },
                    "collection_time" : "1 hour, 12 minutes, 23 seconds and 558 milliseconds",
                    "collection_count" : 26580
                },
                "mem" : {
                    "heap_used" : "20.1gb",
                    "non_heap_used_in_bytes" : 46931968,
                    "heap_committed_in_bytes" : 25612779520,
                    "heap_used_in_bytes" : 21659637592,
                    "heap_committed" : "23.8gb",
                    "non_heap_used" : "44.7mb",
                    "non_heap_committed_in_bytes" : 70365184,
                    "non_heap_committed" : "67.1mb",
                    "pools" : {
                        "Code Cache" : {
                            "peak_max" : "48mb",
                            "peak_max_in_bytes" : 50331648,
                            "peak_used" : "11.8mb",
                            "max_in_bytes" : 50331648,
                            "max" : "48mb",
                            "used" : "11.7mb",
                            "used_in_bytes" : 12313344,
                            "peak_used_in_bytes" : 12435904
                        },
                        "Par Survivor Space" : {
                            "peak_max" : "149.7mb",
                            "peak_max_in_bytes" : 157024256,
                            "peak_used" : "149.7mb",
                            "max_in_bytes" : 157024256,
                            "max" : "149.7mb",
                            "used" : "134.9mb",
                            "used_in_bytes" : 141537456,
                            "peak_used_in_bytes" : 157024256
                        },
                        "CMS Old Gen" : {
                            "peak_max" : "22.5gb",
                            "peak_max_in_bytes" : 24199495680,
                            "peak_used" : "21.6gb",
                            "max_in_bytes" : 24199495680,
                            "max" : "22.5gb",
                            "used" : "19.1gb",
                            "used_in_bytes" : 20601920280,
                            "peak_used_in_bytes" : 23224380656
                        },
                        "CMS Perm Gen" : {
                            "peak_max" : "82mb",
                            "peak_max_in_bytes" : 85983232,
                            "peak_used" : "33mb",
                            "max_in_bytes" : 85983232,
                            "max" : "82mb",
                            "used" : "33mb",
                            "used_in_bytes" : 34618624,
                            "peak_used_in_bytes" : 34618624
                        },
                        "Par Eden Space" : {
                            "peak_max" : "1.1gb",
                            "peak_max_in_bytes" : 1256259584,
                            "peak_used" : "1.1gb",
                            "max_in_bytes" : 1256259584,
                            "max" : "1.1gb",
                            "used" : "873.7mb",
                            "used_in_bytes" : 916179856,
                            "peak_used_in_bytes" : 1256259584
                        }
                    }
                },
                "threads" : {
                    "count" : 344,
                    "peak_count" : 566
                }
            }
        }
    },
    "cluster_name" : "production"
}"""
        self.collector.flatten(json.loads(stats))
        self.collector_hostname_only.flatten(json.loads(stats))
        self.result = self.collector.protocol.output
        self.result_hostname_only = self.collector_hostname_only.protocol.output


    def test_basic(self):
        """
        There is a value for the JVM uptime on the ES data node.
        """
        self.assertEqual(109840215,
                         self.result['es.nodes.es-data.example.org.jvm.uptime'][0])
        self.assertEqual(109840215,
                         self.result_hostname_only['es.nodes.es-data.jvm.uptime'][0])


    def test_noSequence(self):
        """
        No value should be a sequence.
        """
        for key, (value, timestamp) in self.result.iteritems():
            self.assertFalse(hasattr(value, "index"),
                             "Key %s has a sequence value %r" % (key, value))


    def test_loadAverage(self):
        """
        Load averages are in a list and should get numbered paths.
        """
        self.assertEqual(
            8.15,
            self.result['es.nodes.es-data.example.org.os.load_average.0'][0])
        self.assertEqual(
            10.78,
            self.result['es.nodes.es-data.example.org.os.load_average.1'][0])
        self.assertEqual(
            11.92,
            self.result['es.nodes.es-data.example.org.os.load_average.2'][0])
        self.assertEqual(
            8.15,
            self.result_hostname_only['es.nodes.es-data.os.load_average.0'][0])
        self.assertEqual(
            10.78,
            self.result_hostname_only['es.nodes.es-data.os.load_average.1'][0])
        self.assertEqual(
            11.92,
            self.result_hostname_only['es.nodes.es-data.os.load_average.2'][0])


    def test_fsData(self):
        """
        Filesystem data yields a path per item.
        """
        self.assertEqual(
            1194699919360,
            self.result['es.nodes.es-data.example.org.fs.data.0.available'][0])
        self.assertEqual(
            1194699919360,
            self.result_hostname_only['es.nodes.es-data.fs.data.0.available'][0])


    def test_jvmMemPools(self):
        """
        The paths of JVM memory pools metric should have spaces removed.
        """
        self.assertIn('es.nodes.es-data.example.org.jvm.mem.pools.CMSPermGen.max',
                      self.result)
        self.assertIn('es.nodes.es-data.jvm.mem.pools.CMSPermGen.max',
                      self.result_hostname_only)


    def test_indicesForDataNode(self):
        """
        Data nodes have indices paths.
        """
        self.assertIn(
                'es.nodes.es-data.example.org.indices.docs.count',
                self.result)
        self.assertIn(
                'es.nodes.es-data.indices.docs.count',
                self.result_hostname_only)


    def test_noIndicesForNonDataNode(self):
        """
        Non data nodes do not have indices paths.
        """
        self.assertNotIn(
                'es.nodes.es-proxy.indices.docs.count',
                self.result)
        self.assertNotIn(
                'es.nodes.logstash.indices.docs.count',
                self.result)
        self.assertNotIn(
                'es.nodes.graylog2.indices.docs.count',
                self.result)


    def test_timestampInherited(self):
        """
        The timestamp is inherited from higher up in the structure.
        """
        self.assertEqual(
                1354643578.330,
                self.result['es.nodes.es-proxy.http.current_open'][1])


    def test_timestampSibling(self):
        """
        If a dict has a timestamp, it is used for sibling structures.
        """
        self.assertEqual(
                1354643578.331,
                self.result['es.nodes.es-proxy.process.mem.share'][1])



class ElasticSearchHealthGraphiteServiceTest(unittest.TestCase):

    def setUp(self):
        self.collector = ElasticSearchHealthGraphiteService(
            'http://localhost:9200/')
        self.collector.protocol = FakeGraphiteProtocol()
        stats = """
{
    "cluster_name": "elasticsearch",
    "status": "green",
    "timed_out": false,
    "number_of_nodes": 5,
    "number_of_data_nodes": 4,
    "active_primary_shards": 65,
    "active_shards": 130,
    "relocating_shards": 0,
    "initializing_shards": 0,
    "unassigned_shards": 0

}"""

        data = json.loads(stats)
        self.collector.flatten(data)
        self.result = self.collector.protocol.output


    def test_active_shards(self):
        """
        Active shards metric is present.
        """
        self.assertEqual(130, self.result['es.cluster.active_shards'][0])


    def test_timestamp(self):
        """
        Metrics have a timestamp.
        """
        self.assertApproximates(time.time(),
                                self.result['es.cluster.active_shards'][1],
                                3)


    def test_status(self):
        """
        A status is given its own metric.
        """
        self.assertEqual(1, self.result['es.cluster.status.green'][0])
        self.assertEqual(0, self.result['es.cluster.status.yellow'][0])
        self.assertEqual(0, self.result['es.cluster.status.red'][0])


    def test_statusYellow(self):
        """
        For status yellow to other metrics are 0.
        """
        stats = """{"status": "yellow"}"""
        data = json.loads(stats)
        self.collector.flatten(data)
        self.result = self.collector.protocol.output

        self.assertEqual(0, self.result['es.cluster.status.green'][0])
        self.assertEqual(1, self.result['es.cluster.status.yellow'][0])
        self.assertEqual(0, self.result['es.cluster.status.red'][0])
