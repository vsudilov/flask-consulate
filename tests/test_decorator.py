# coding: utf-8

import unittest
import httpretty
import requests

from requests.exceptions import ConnectionError
from six import next

from flask_consulate.decorators import with_retry_connections
from flask_consulate.exceptions import ConsulConnectionError


class TestDecorator(unittest.TestCase):
    """
    Test the function decorators that are distributed in flask.ext.consul
    """

    @httpretty.activate
    def test_with_retry_connections(self):
        """
        Ensure that the decorator `with_retry_connections` works as advertised;
        functions should be retried if they fail with ConnectionError for a
        default maximum of 3 times before giving up
        """

        urls = (url for url in [
            'http://fake.com',
            'http://fake.com',
            'http://real.com',
        ])

        httpretty.register_uri(
            httpretty.GET,
            'http://real.com',
            body="OK"
        )

        def callback(*args, **kwargs):
            raise ConnectionError

        httpretty.register_uri(
            httpretty.GET,
            "http://fake.com",
            body=callback,
        )

        @with_retry_connections()
        def GET_request(urls):
            """
            This function will attempt to contact 3 urls: the first two
            should intentionally cause a ConnectionError, and the third
            will be caught by httpretty and serve a valid response
            """
            u = next(urls)
            return requests.get(u)

        r = GET_request(urls)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "OK")

    def test_failing_retry_connections(self):
        """
        Test that the proper exception is raised after retrying and failing
        """

        @with_retry_connections()
        def GET_request():
            """
            This function will attempt to contact 3 urls: the first two
            should intentionally cause a ConnectionError, and the third
            will be caught by httpretty and serve a valid response
            """
            raise ConnectionError

        with self.assertRaises(ConsulConnectionError):
            GET_request()
