# coding: utf-8

import os
import unittest

from httpretty import HTTPretty
from flask import Flask

from flask_consulate import Consul


class MockConsulKV:
    """
    Context manager that mocks a consul KV response.
    """

    def __enter__(self):
        """
        Defines the behaviour for __enter__
        """

        HTTPretty.enable()
        host = os.environ.get('CONSUL_HOST', 'localhost')
        service_name = os.environ.get('SERVICE', 'generic_service')
        environ_name = os.environ.get('ENVIRONMENT', 'generic_environment')

        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://{host}:8500/v1/kv/config/{service}/{environment}/".format(
                host=host,
                service=service_name,
                environment=environ_name,
            ),
            body='''[
    {{
        "CreateIndex": 5729,
        "Flags": 0,
        "Key": "config/{service}/{environment}/cfg_1",
        "LockIndex": 0,
        "ModifyIndex": 5729,
        "Value": "Y29uc3VsXzE="
    }},
    {{
        "CreateIndex": 5730,
        "Flags": 0,
        "Key": "config/{service}/{environment}/cfg_3",
        "LockIndex": 0,
        "ModifyIndex": 5730,
        "Value": "Y29uc3VsXzM="
    }}
]'''.format(service=service_name, environment=environ_name),
        )

    def __exit__(self, etype, value, traceback):
        """
        Defines the behaviour for __exit__

        :param etype: exit type
        :param value: exit value
        :param traceback: the traceback for the exit
        """

        HTTPretty.reset()
        HTTPretty.disable()


class TestApplyRemoteConfig(unittest.TestCase):
    """
    Test that the config is properly applied by the extension
    """

    def create_app(self):
        """
        Create a basic flask.Flask application
        """
        app = Flask('tests')
        app.config.update({
            'cfg_1': 'local_1',
            'cfg_2': 'local_2',
            'cfg_4': {'inner': 'value'},
        })
        return app

    def test_config_with_defaults(self):
        """
        Ensures that application config is loaded by consul using the default
        namespace and host
        """

        with MockConsulKV():
            app = self.create_app()
            consul = Consul(app)
            consul.apply_remote_config()

        self.assertEqual(app.config['cfg_1'], 'consul_1')
        self.assertEqual(app.config['cfg_3'], 'consul_3')
        self.assertEqual(app.config['cfg_4'], {'inner': 'value'})

    def test_config_with_environ(self):
        """
        Ensures that application config is loaded by consul using host and
        namespace defined by environmental variables
        """

        os.environ['CONSUL_HOST'] = "consul.adsabs"
        os.environ['SERVICE'] = "sample_application"
        os.environ['ENVIRONMENT'] = "testing"

        with MockConsulKV():
            app = self.create_app()
            consul = Consul(app)
            consul.apply_remote_config()

        del os.environ['CONSUL_HOST']
        del os.environ['SERVICE']
        del os.environ['ENVIRONMENT']

        self.assertEqual(app.config['cfg_1'], 'consul_1')
        self.assertEqual(app.config['cfg_3'], 'consul_3')
