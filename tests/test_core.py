import unittest
from flask import Flask
import httpretty

from flask.ext.consulate import Consul


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

    @httpretty.activate
    def test_session(self):
        """
        Ensures that the session has the expected connectivity
        """

        httpretty.register_uri(
            httpretty.GET,
            "http://localhost:8500/v1/status/leader",
            body="localhost:8300",
        )
        app = self.create_app()
        Consul(app, test_connection=True)


if __name__ == '__main__':
    unittest.main()

