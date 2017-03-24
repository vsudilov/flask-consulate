#!/usr/bin/env python
"""
flask-consulate
-------------

flask extension that provides an interface to consul via a flask.app
"""
from setuptools import setup
import os
import sys
import re
if os.environ.get('USER', '') == 'vagrant':
    del os.link

major, minor1, minor2, release, serial =  sys.version_info

if major == 2:
    dnspython = "dnspython"
elif major == 3:
    dnspython = "dnspython3"

readfile_kwargs = {"encoding": "utf-8"} if major >= 3 else {}


def readfile(filename):
    with open(filename, **readfile_kwargs) as fp:
        contents = fp.read()
    return contents

version_regex = re.compile("__version__ = \"(.*?)\"")
contents = readfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "flask_consulate.py"))

version = version_regex.findall(contents)[0]

setup(
    name='flask-consulate',
    version=version,
    url='http://github.com/vsudilov/flask-consulate/',
    license='MIT',
    author='Vladimir Sudilovsky',
    author_email='vsudilovsky@gmail.com',
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
        'consulate',
        'Flask',
        'requests>=2.7.0',
        dnspython,
        'flask-testing',
        'httpretty',
        'mock',
        'nose',
        'six',
        'coveralls'
    ],
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

