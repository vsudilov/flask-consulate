===============
flask-consulate
===============

.. image:: https://travis-ci.org/wemake-services/flask-consulate.svg?branch=master
   :target: https://travis-ci.org/wemake-services/flask-consulate

.. image:: https://coveralls.io/repos/wemake-services/flask-consulate/badge.svg?branch=master
   :target: https://coveralls.io/github/wemake-services/flask-consulate?branch=master

Synopsis
========

``flask_consulate`` is an extension for `consulate`_.
This extension performs some application specific tasks, such as:

1. Builtin retrying of connections to a single host, which may be useful
when trying to resolve a consul cluster by hostname or behind a load balancer
2. writes config values found in a namespaced consul kv store into ``app.config``

Testing
=======

We use ``py.test`` and ``tox`` for testing.
Run ``python setup.py test`` to test this project.
And ``tox`` to run tests across all environments.

.. _`consulate`: https://github.com/gmr/consulate
