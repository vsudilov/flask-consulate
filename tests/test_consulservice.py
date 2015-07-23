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

    @mock.patch('flask.ext.consulate.netifaces')
    def test_set_ns(self, mocked):
        """
        set_ns() should set ConsulService.resolver.nameservers to the ip
        associated with a specified network interface
        """
        mocked.interfaces.return_value = ['docker0']
        mocked.ifaddresses.return_value = {
            mocked.AF_INET: [{'addr': '192.168.1.1'}]
        }
        cs = ConsulService('consul://', discover_ns='docker0')
        self.assertEqual(cs.resolver.nameservers, ['192.168.1.1'])
        with self.assertRaisesRegexp(AssertionError, "Unknown iface eth0"):
            cs.set_ns(iface='eth0')

    @skip("!! Test not implemented !!")
    def test_resolve(self):
        """
        resolve() should return a list of string formatted service endpoints
        and set ConsulService.endpoints
        """
        pass

    @mock.patch('flask.ext.consulate.ConsulService._resolve')
    def test_baseurl(self, mocked):
        """
        the class property base_url should call _resolve() and return a random
        element from that result list
        """
        mocked.return_value = ["addr-{}:80".format(i) for i in range(50)]
        cs = ConsulService("consul://")
        urls = [cs.base_url, cs.base_url, cs.base_url]
        self.assertNotEqual(
            urls,
            set(urls),
            msg="testing random.Choice here, which might cause this to break "
                "a negligible fraction of the time"
        )
        for u in urls:
            self.assertIn(u, mocked.return_value)
        self.assertEqual(mocked.call_count, 3)

    @mock.patch('flask.ext.consulate.requests.Session')
    def test_request(self, mocked):
        """
        the ConsulService.request should be a thin wrapper around
        requests
        """
        instance = mocked.return_value
        with mock.patch('flask.ext.consulate.ConsulService._resolve') as r:
            r.return_value = ["http://base_url:80/"]
            cs = ConsulService("consul://")
            cs.get('/v1/status')
            instance.request.assert_called_with(
                'GET',
                'http://base_url:80/v1/status',
                timeout=(1, 30),
            )




