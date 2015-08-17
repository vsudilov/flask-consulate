#!/usr/bin/env python
"""
flask-consulate
-------------

flask extension that provides an interface to consul via a flask.app
"""
from setuptools import setup
from pip.download import PipSession
from pip.req import parse_requirements
import os
if os.environ.get('USER', '') == 'vagrant':
    del os.link
from _version import __version__

# parse_requirements() returns generator of pip.req.InstallRequirement objects
reqs = parse_requirements('requirements.txt', session=PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in reqs]

setup(
    name='flask-consulate',
    version=__version__,
    url='http://github.com/adsabs/flask-consulate/',
    license='MIT',
    author='Vladimir Sudilovsky',
    author_email='vsudilovsky@cfa.harvard.edu',
    description='flask extension that provides an interface to consul via a flask.app',
    long_description=__doc__,
    py_modules=['flask_consulate'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=reqs,
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

