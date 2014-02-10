#!/usr/bin/env python

from setuptools import setup

setup(name='vor',
      version='0.0.1',
      description='Services for gatheric metrics to send to Graphite',
      maintainer='Ralph Meijer',
      maintainer_email='ralphm@ik.nu',
      url='http://github.com/ralphm/vor',
      license='MIT',
      platforms='any',
      packages=[
          'vor',
          'vor.test',
      ],
      zip_safe=False,
      install_requires=[
          'Twisted >= 12.0.0',
          'simplejson',
          'txredis',
      ],
)
