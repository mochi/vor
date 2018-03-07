News
====

This project uses `CalVer <http://calver.org>`_ with a strict backwards
compatibility policy. The third digit is only for regressions.

Changes for the upcoming release can be found in the `vor/newsfragments`
directory.

..
   Do *NOT* add changelog entries here!

   This changelog is managed by towncrier and is compiled at release time from
   the news fragments directory.

.. towncrier release notes start

Vor 18.0.0rc1 (2018-03-07)
==========================

Features
--------

- vor.elasticsearch now supports the Elasticsearch 1.0 API (#1)
- The new module vor.beanstalk adds support for Beanstalk stats. (#2)
- vor.elasticsearch.ElasticSearchNodeStatsGraphiteService now has a boolean
  `hostname_only` parameter to strip the domain off the node's name. (#4, #6)
- The new vor.kafka module adds support for Kafka Consumer Offset polling. (#5)
- The new vor.elasticsearch.ElasticSearchIndicesStatsGraphiteService provides a
  poller for the Indices Stats API. (#7, #9)
- vor.elasticsearch now supports basic authentication and (non-validated) https
  for its pollers. (#10)


Fixes
-----

- vor.elasticsearch pollers now remove spaces from metric names. (#8)


0.0.1 (2014-02-10)
==================

First release
