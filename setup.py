#!/usr/bin/env python
"""
flask-consulate
-------------

flask extension that provides an interface to consul via a flask.app
"""

import sys

from setuptools import setup, find_packages


# Dependencies:

if sys.version_info[0] == 2:
    dnspython = 'dnspython'
elif sys.version_info[0] == 3:
    dnspython = 'dnspython3'
else:
    raise ValueError('Unsupported python version')

INSTALL_REQUIRES = [
    'consulate',
    'Flask',
    'requests>=2.7.0',
    'six',
    dnspython,
]

TESTS_REQUIRE = [
    'httpretty',
    'mock',
    'coveralls',
    'coverage',
    'pytest',
]

SETUP_REQUIRES = [
    'pytest-runner',
]


setup(
    name='flask-consulate',
    version='0.2.0',
    url='http://github.com/vsudilov/flask-consulate',
    license='MIT',
    author='Vladimir Sudilovsky',
    author_email='vsudilovsky@gmail.com',

    description='flask extension that provides an interface to consul via a flask app',
    long_description=__doc__,

    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',

    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={
        'test': TESTS_REQUIRE,
    },
    test_suite='tests',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

