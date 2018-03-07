Vör
===

|pypi|
|travis|


What is this?
-------------

Vör is a set of services for gathering metrics by polling systems and
delivering them to graphite.

Currently there is support for polling metrics from Elasticsearch and Redis.


Requirements
------------

- Python 2.7 or pypy equivalent
- Twisted 16.0.0 or later
- incremental 16.9.0 or later
- treq 16.20.0 or later for Elasticsearch support
- txredis for Redis support
- pybeanstalk for Beanstalk support


Copyright and Warranty
----------------------

The code in this distribution started as an internal tool at Mochi Media and
is made available under the MIT License. See the included `LICENSE <LICENSE>`_
file for details.


Contributors
------------

- Christopher Zorn
- Zack Dever
- Dana Powers


Author
------

Ralph Meijer
<mailto:ralphm@ik.nu>
<xmpp:ralphm@ik.nu>


Name
----

In Norse mythology, Vör is a goddess associated with wisdom. She is described
as "wise and inquiring, so that nothing can be concealed from her".


.. |pypi| image:: http://img.shields.io/pypi/v/vor.svg
.. _pypi: https://pypi.python.org/pypi/vor

.. |travis| image:: https://travis-ci.org/mochi/vor.svg?branch=master
.. _travis: https://travis-ci.org/mochi/vor
