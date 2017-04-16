# -*- coding: utf-8 -*-

import os
import json

import consulate

from six import iteritems

from flask_consulate.decorators import with_retry_connections


class Consul(object):
    """
    The Consul flask.ext object is responsible for connecting and querying
    consul (using gmr/consulate as the underlying client library).
    """

    def __init__(self, app=None, **kwargs):
        """
        Initialize the flask extension

        :param app: flask.Flask application instance
        :param kwargs:
            consul_host: host to connect to, falling back to environmental
                        variable $CONSUL_HOST, then 'localhost'
            consul_port: port, falling back to $CONSUL_PORT, then 8500
            healthcheck: healthcheck that will be registered
            max_tries: integer number of attempts to make to connect to
                        consul_host. Useful if the host is an alias for
                        the consul cluster
        :return: None
        """
        self.kwargs = kwargs if kwargs else {}
        self.app = None

        self.host = self.kwargs.get('consul_host') or \
            os.environ.get('CONSUL_HOST', 'localhost')
        self.port = self.kwargs.get('consul_port') or \
            os.environ.get('CONSUL_PORT', 8500)
        self.max_tries = self.kwargs.get('max_tries', 3)

        self.session = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'consul' in app.extensions:
            raise RuntimeError('Flask application already initialized')
        app.extensions['consul'] = self

        self.session = self._create_session(
            test_connection=self.kwargs.get('test_connection', False),
        )

    @with_retry_connections()
    def _create_session(self, test_connection=False):
        """
        Create a consulate.session object, and query for its leader to ensure
        that the connection is made.

        :param test_connection: call .leader() to ensure that the connection
            is valid
        :type test_connection: bool
        :return consulate.Session instance
        """
        session = consulate.Session(host=self.host, port=self.port)
        if test_connection:
            session.status.leader()
        return session

    @with_retry_connections()
    def apply_remote_config(self, namespace=None):
        """
        Applies all config values defined in consul's kv store to self.app.

        There is no guarantee that these values will not be overwritten later
        elsewhere.

        :param namespace: kv namespace/directory. Defaults to
                DEFAULT_KV_NAMESPACE
        :return: None
        """

        if namespace is None:
            namespace = "config/{service}/{environment}/".format(
                service=os.environ.get('SERVICE', 'generic_service'),
                environment=os.environ.get('ENVIRONMENT', 'generic_environment')
            )

        for k, v in iteritems(self.session.kv.find(namespace)):
            k = k.replace(namespace, '')
            try:
                self.app.config[k] = json.loads(v)
            except (TypeError, ValueError):
                self.app.logger.warning("Couldn't de-serialize {} to json, using raw value".format(v))
                self.app.config[k] = v

            msg = "Set {k}={v} from consul kv '{ns}'".format(
                k=k,
                v=v,
                ns=namespace,
            )
            self.app.logger.debug(msg)

    @with_retry_connections()
    def register_service(self, **kwargs):
        """
        register this service with consul
        kwargs passed to Consul.agent.service.register
        """
        kwargs.setdefault('name', self.app.name)
        self.session.agent.service.register(**kwargs)
