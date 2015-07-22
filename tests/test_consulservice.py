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
        cs = ConsulService('consul://tag.name.service', discover_ns=False)
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
        cs = ConsulService('consul://')
        self.assertEqual(cs.resolver.nameservers, ['192.168.1.1'])
        with self.assertRaisesRegexp(AssertionError, "Unknown iface eth1"):
            cs.set_ns(iface='eth1')

    @skip("!! Test not implemented !!")
    def test_resolve(self):
        """
        resolve() should return a list of string formatted service endpoints
        and set ConsulService.endpoints
        """
        pass

