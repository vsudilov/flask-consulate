import unittest
import httpretty
import requests
try:
    from flask.ext.consulate import with_retry_connections, \
        ConsulConnectionError
except ImportError:
    import sys
    sys.path.append('..')
    from flask_consulate import with_retry_connections, ConsulConnectionError


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

        urls = (
            url for url in ['http://fake', 'http://fake', 'http://real.com']
        )

        httpretty.register_uri(
            httpretty.GET,
            "http://real.com",
            body="OK"
        )

        @with_retry_connections()
        def GET_request(urls):
            """
            This function will attempt to contact 3 urls: the first two
            should intentionally cause a ConnectionError, and the third
            will be caught by httpretty and serve a valid response
            """
            u = urls.next()
            return requests.get(u)

        r = GET_request(urls)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "OK")

    def test_failing_retry_connections(self):
        """
        Test that the proper exception is raised after retrying and failing
        after 3 times
        """
        urls = (
            url for url in ['http://fake', 'http://fake', 'http://fake']
        )

        @with_retry_connections()
        def GET_request(urls):
            """
            This function will attempt to contact 3 urls: the first two
            should intentionally cause a ConnectionError, and the third
            will be caught by httpretty and serve a valid response
            """
            u = urls.next()
            return requests.get(u)

        with self.assertRaises(ConsulConnectionError):
            GET_request(urls)


if __name__ == '__main__':
    unittest.main()