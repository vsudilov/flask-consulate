"""
Test ConsulService
"""
from flask.ext.consulate import ConsulService
from unittest import TestCase, skip
import mock


class TestConsulService(TestCase):
    """
    Test core functionality of the ConsulService class, which is responsible
    for querying a DNS server to find a service uri
    """

    def test_init(self):
        """
        an initialized ConsulService object should parse the service URI
        """
        cs = ConsulService('consul://tag.name.service')
        self.assertEqual(cs.service, 'tag.name.service')


    @skip("!! Test not implemented !!")
    def test_resolve(self):
        """
        resolve() should return a list of string formatted service endpoints
        and set ConsulService.endpoints
        """
        pass

    def test_baseurl(self):
        """
        the class property base_url should call _resolve() and return an
        element from that result list
        """
        cs = ConsulService("consul://")
        cs.endpoints = ("addr-{}:80".format(i) for i in range(50))
        urls = [cs.base_url, cs.base_url, cs.base_url]
        self.assertEquals(
            ["addr-0:80", "addr-1:80", "addr-2:80"],
            urls
        )

    @mock.patch('flask.ext.consulate.requests.Session')
    def test_request(self, mocked):
        """
        the ConsulService.request should be a thin wrapper around
        requests
        """
        instance = mocked.return_value
        cs = ConsulService("consul://")
        cs.endpoints = iter(("http://base_url:80/",))
        cs.get('/v1/status')
        instance.request.assert_called_with(
            'GET',
            'http://base_url:80/v1/status',
            timeout=(1, 30),
        )




