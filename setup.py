#!/usr/bin/env python

from setuptools import setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(name='vor',
      description='Services for gathering metrics to send to Graphite',
      long_description=long_description,
      maintainer='Ralph Meijer',
      maintainer_email='ralphm@ik.nu',
      url='http://github.com/ralphm/vor',
      license='MIT',
      platforms='any',
      classifiers=[
          'Programming Language :: Python :: 2.7',
      ],
      packages=[
          'vor',
          'vor.test',
      ],
      zip_safe=False,
      setup_requires=[
          'incremental>=16.9.0',
      ],
      use_incremental=True,
      install_requires=[
          'incremental>=16.9.0',
          'Twisted[tls] >= 16.0.0',
      ],
      extras_require={
          'elasticsearch': [
              'treq >= 16.12.0',
          ],
          'redis': [
              'txredis',
          ],
          'beanstalk': [
              'pybeanstalk',
          ],
          'dev': [
              'pyflakes',
              'coverage',
              'towncrier',
          ],
      },
)
