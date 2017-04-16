===============
flask-consulate
===============

.. image:: https://travis-ci.org/vsudilov/flask-consulate.svg?branch=master
   :target: https://travis-ci.org/vsudilov/flask-consulate

.. image:: https://coveralls.io/repos/vsudilov/flask-consulate/badge.svg?branch=master
   :target: https://coveralls.io/github/vsudilov/flask-consulate?branch=master

Synopsis
========

``flask_consulate`` is an extension for `consulate`_.
This extension performs some application specific tasks, such as:

1. Builtin retrying of connections to a single host, which may be useful
when trying to resolve a consul cluster by hostname or behind a load balancer
2. writes config values found in a namespaced consul kv store into ``app.config``

Example
=======

This example shows several things: 

1. how to register a ``Consul`` service
2. how to implement a health-check
3. how to receive configuration from ``Consul``'s KV-storage.

.. code-block:: python
    
    from flask import Flask
    from flask_consulate import Consul

    app = Flask(__name__)
    
    
    @app.route('/healthcheck')
    def health_check():
        """
        This function is used to say current status to the Consul.
        Format: https://www.consul.io/docs/agent/checks.html
    
        :return: Empty response with status 200, 429 or 500
        """
        # TODO: implement any other checking logic.
        return '', 200
    
    
    # Consul
    # This extension should be the first one if enabled:
    consul = Consul(app=app)
    # Fetch the conviguration:
    consul.apply_remote_config(namespace='mynamespace/')
    # Register Consul service:
    consul.register_service(
        name='my-web-app',
        interval='10s',
        tags=['webserver', ],
        port=5000,
        httpcheck='http://localhost:5000/healthcheck'
    )
    
Now you can run your server. It will be shown in the ``Consul UI``, it will also receive a health-check request each 10 seconds.

Testing
=======

We use ``py.test`` and ``tox`` for testing.
Run ``python setup.py test`` to test this project.
And ``tox`` to run tests across all environments.

.. _`consulate`: https://github.com/gmr/consulate
