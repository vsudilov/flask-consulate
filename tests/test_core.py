import unittest
from flask import Flask
from flask.ext.testing import TestCase
import httpretty
try:
    from flask.ext.consulate import Consul
except ImportError:
    import sys
    sys.path.append('..')
    from flask_consulate import Consul


class TestFlaskConsulate(TestCase):
    """
    Tests the core functionality of flask.ext.consulate.Consul, including
    instansiation and class methods
    """

    @httpretty.activate
    def create_app(self):
        app = Flask('tests')
        app.config.update({
            'cfg_1': 'local_1',
            'cfg_2': 'local_2',
        })

        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8500/v1/status/leader",
            body="localhost:8300",
        )

        self.consul = Consul(test_connection=True)
        self.consul.init_app(app)
        return app

    def test_extension_registration(self):
        """
        Tests that the consul extension has been registered and initialized
        """
        self.assertIn('consul', self.app.extensions)
        self.assertEqual(self.consul, self.app.extensions['consul'])

    @httpretty.activate
    def test_apply_remote_config(self):
        """
        Tests that Consul.apply_remote_config properly overwrites the
        application's config
        """
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8500/v1/kv/config/generic_service/generic_environment/",
            body='''[
    {
        "CreateIndex": 5729,
        "Flags": 0,
        "Key": "config/generic_service/generic_environment/cfg_1",
        "LockIndex": 0,
        "ModifyIndex": 5729,
        "Value": "Y29uc3VsXzE="
    },
    {
        "CreateIndex": 5730,
        "Flags": 0,
        "Key": "config/generic_service/generic_environment/cfg_3",
        "LockIndex": 0,
        "ModifyIndex": 5730,
        "Value": "Y29uc3VsXzM="
    }
]''',
        )
        self.consul.apply_remote_config()
        self.assertEqual(self.app.config['cfg_1'], 'consul_1')
        self.assertEqual(self.app.config['cfg_2'], 'local_2')
        self.assertEqual(self.app.config['cfg_3'], 'consul_3')

if __name__ == '__main__':
    unittest.main()

