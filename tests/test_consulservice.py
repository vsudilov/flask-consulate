# coding: utf-8

import mock

from unittest import TestCase, skip

from flask_consulate import ConsulService


class TestConsulService(TestCase):
    """
    Test core functionality of the ConsulService class, which is responsible
    for querying a DNS server to find a service uri
    """

    def test_init(self):
        """
        an initialized ConsulService object should parse the service URI
        """
        cs = ConsulService('consul://tag.name.service', nameservers=['1'])
        self.assertEqual(cs.service, 'tag.name.service')
        cs.resolver.nameservers = ['1']
        with self.assertRaises(AssertionError):
            ConsulService('http://')

    @skip('!! Test not implemented !!')
    def test_resolve(self):
        """
        resolve() should return a list of string formatted service endpoints
        and set ConsulService.endpoints
        """
        pass

    @mock.patch('flask_consulate.ConsulService._resolve')
    def test_baseurl(self, mocked):
        """
        the class property base_url should call _resolve() and return the last
        element from that result list
        """
        mocked.side_effect = lambda: ['addr-{}:80'.format(i) for i in range(5)]
        cs = ConsulService('consul://')
        urls = [cs.base_url, cs.base_url, cs.base_url]
        self.assertEqual(mocked.call_count, 3)
        self.assertEquals(
            ['addr-4:80', 'addr-4:80', 'addr-4:80'],
            urls
        )

    @mock.patch('flask_consulate.ConsulService._resolve')
    @mock.patch('flask_consulate.service.requests.Session')
    def test_request(self, mocked, mocked_resolve):
        """
        the ConsulService.request should be a thin wrapper around
        requests
        """
        mocked_resolve.return_value = ['http://base_url:80/']
        instance = mocked.return_value
        cs = ConsulService('consul://')
        cs.get('/v1/status')
        instance.request.assert_called_with(
            'GET',
            'http://base_url:80/v1/status',
            timeout=(1, 30),
        )
