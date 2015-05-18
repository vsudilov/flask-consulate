#!/usr/bin/env python
"""
flask-consulate
-------------

flask extension that provides an interface to consul via a flask.app
"""
from setuptools import setup


setup(
    name='flask-consulate',
    version='0.0.1',
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
    install_requires=[
        'flask',
        'consulate==0.4.0',
    ],
    test_suite='tests',
    tests_require = [
        'flask-testing',
        'httpretty',
    ],
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

