#!/usr/bin/env python
"""
flask-consulate
-------------

flask extension that provides an interface to consul via a flask.app
"""
from setuptools import setup
import os
if os.environ.get('USER', '') == 'vagrant':
    del os.link

setup(
    name='flask-consulate',
    version="0.1.1",
    url='http://github.com/adsabs/flask-consulate/',
    license='MIT',
    author='Vladimir Sudilovsky',
    author_email='vsudilovsky@cfa.harvard.edu',
    description='flask extension that provides an interface to consul via a flask app',
    long_description=__doc__,
    py_modules=['flask_consulate'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'consulate==0.4.0',
        'Flask',
        'requests>=2.7.0',
        'dnspython',
        'flask-testing',
        'httpretty',
        'mock',
        'nose',
        'coveralls'
    ],
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

