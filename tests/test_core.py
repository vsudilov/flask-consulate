# coding: utf-8

import unittest
import httpretty
import mock

from flask import Flask

from flask_consulate import Consul
from flask_consulate.exceptions import ConsulConnectionError


class TestFlaskConsulate(unittest.TestCase):
    """
    Tests the core functionality of flask.ext.consulate.Consul, including
    instansiation and class methods
    """

    def create_app(self):
        """
        Create a basic flask.Flask application
        """
        app = Flask('tests')
        app.config.update({
            'cfg_1': 'local_1',
            'cfg_2': 'local_2',
        })
        return app

    def test_extension_registration(self):
        """
        Tests that the consul extension has been registered and initialized
        """
        app = self.create_app()
        consul = Consul(app)
        self.assertIn('consul', app.extensions)
        self.assertEqual(consul, app.extensions['consul'])

        app = self.create_app()
        consul = Consul()
        consul.init_app(app)
        self.assertIn('consul', app.extensions)
        self.assertEqual(consul, app.extensions['consul'])

    def test_session(self):
        """
        Ensures that the session has the expected connectivity
        """
        httpretty.enable()

        httpretty.register_uri(
            httpretty.GET,
            'http://consul.internal:8501/v1/status/leader',
            body="localhost:8300",
        )
        app = self.create_app()
        consul = Consul(
            app,
            consul_host='consul.internal',
            consul_port='8501',
            test_connection=True
        )
        self.assertIsNotNone(consul)

        httpretty.disable()
        httpretty.reset()

        app = self.create_app()
        self.assertRaises(
            ConsulConnectionError,
            lambda: Consul(
                app,
                consul_host='consul.internal',
                consul_port='8501',
                test_connection=True
            ),
        )

    def test_register_service(self):
        """
        Service registration should call the underlying consulate register api
        """
        httpretty.enable()

        httpretty.register_uri(
            httpretty.GET,
            'http://consul.internal:8500/v1/status/leader',
            body="localhost:8300",
        )
        app = self.create_app()
        with mock.patch('consulate.Session') as mocked:
            consul = Consul(app)
            consul.register_service()
            self.assertEqual(mocked.return_value.agent.service.register.call_count, 1)

        httpretty.disable()
        httpretty.reset()
