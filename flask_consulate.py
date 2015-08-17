import os
import consulate
import time
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from dns.resolver import Resolver
from urlparse import urljoin
from _version import __version__


class ConsulConnectionError(ConnectionError):
    """A connection error related to Consul occured"""


def with_retry_connections(max_tries=3, sleep=0.05):
    """
    Decorator that wraps an entire function in a try/except clause. On
    requests.exceptions.ConnectionError, will re-run the function code
    until success or max_tries is reached.

    :param max_tries: maximum number of attempts before giving up
    :param sleep: time to sleep between tries, or None
    """
    def decorator(f):
        def f_retry(*args, **kwargs):
            tries = 0
            while 1:
                try:
                    return f(*args, **kwargs)
                except (ConnectionError, ConnectTimeout), e:
                    tries += 1
                    if tries >= max_tries:
                        raise ConsulConnectionError(e)
                    if sleep:
                        time.sleep(sleep)
        return f_retry
    return decorator


class Consul(object):
    """
    The Consul flask.ext object is responsible for connecting and querying
    consul (using gmr/consulate as the underlying client library).
    """

    def __init__(self, app=None, **kwargs):
        """
        Initialize the flask extension

        :param app: flask.Flask application instance
        :param kwargs:
            consul_host: host to connect to, falling back to environmental
                        variable $CONSUL_HOST, then 'localhost'
            max_tries: integer number of attempts to make to connect to
                        consul_host. Useful if the host is an alias for
                        the consul cluster
        :return: None
        """
        self.kwargs = kwargs if kwargs else {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app, **kwargs):
        self.app = app
        self.kwargs.update(kwargs)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'consul' in app.extensions:
            raise RuntimeError("Flask application already initialized")
        app.extensions['consul'] = self

        self.host = self.kwargs.get('consul_host') or \
            os.environ.get('CONSUL_HOST', 'localhost')
        self.max_tries = self.kwargs.get('max_tries', 3)
        self.session = self._create_session(
            test_connection=self.kwargs.get('test_connection', False),
        )

    @with_retry_connections()
    def _create_session(self, test_connection=False):
        """
        Create a consulate.session object, and query for its leader to ensure
        that the connection is made.

        :param test_connection: call .leader() to ensure that the connection
            is valid
        :type test_connection: bool
        :return consulate.Session instance
        """
        session = consulate.Session(host=self.host)
        if test_connection:
            session.status.leader()
        return session

    @with_retry_connections()
    def apply_remote_config(self, namespace=None):
        """
        Applies all config values defined in consul's kv store to self.app.

        There is no guarantee that these values will not be overwritten later
        elsewhere.

        :param namespace: kv namespace/directory. Defaults to
                DEFAULT_KV_NAMESPACE
        :return: None
        """

        if namespace is None:
            namespace = "config/{service}/{environment}/".format(
                service=os.environ.get('SERVICE', 'generic_service'),
                environment=os.environ.get('ENVIRONMENT', 'generic_environment')
            )

        for k, v in self.session.kv.find(namespace).iteritems():
            k = k.replace(namespace, '')
            self.app.config[k] = v
            msg = "Set {k}={v} from consul kv '{ns}'".format(
                k=k,
                v=v,
                ns=namespace,
            )
            self.app.logger.debug(msg)


class ConsulService(object):
    """
    Container for a consul service record
    Example:

        # Consul advertises a service called FOO that is reachable via two URIs:
        # http://10.1.1.1:8001 and http://10.1.1.2:8002
    cs = ConsulService("consul://tag.FOO.service")

        # Set the DNS nameserver to the default docker0 bridge ip
    cs = ConsulService("consul://tag.FOO.server", nameservers=['172.17.42.1'])

        # returns a random choice from the DNS-advertised routes
        # in our case, either http://10.1.1.1:8001 or http://10.1.1.2:8002
    cs.base_url

        # send an http-get to base_url+'/v1/status', re-resolving and
        # re-retrying if that connection failed
    cs.get('/v1/status')

        #Subsequent http requests will now have the "X-Added" header
    cs.session.headers.update({"X-Added": "Value"})
    cs.post('/v1/status')
    """
    def __init__(self, service_uri, nameservers=None):
        """
        :param service_uri: string formatted service identifier
            (consul://production.solr_service.consul)
        :param nameservers: use custom nameservers
        :type nameservers: list
        """
        assert service_uri.startswith('consul://'), "Invalid consul service URI"
        self.service_uri = service_uri
        self.service = service_uri.replace('consul://', '')
        self.resolver = Resolver()
        self.session = requests.Session()
        if nameservers is not None:
            self.resolver.nameservers = nameservers

    def _resolve(self):
        """
        Query the consul DNS server for the service IP and port
        """
        endpoints = {}
        r = self.resolver.query(self.service, 'SRV')
        for rec in r.response.additional:
            name = rec.name.to_text()
            addr = rec.items[0].address
            endpoints[name] = {'addr': addr}
        for rec in r.response.answer[0].items:
            name = '.'.join(rec.target.labels)
            endpoints[name]['port'] = rec.port
        return [
            "http://{ip}:{port}".format(
                ip=v['addr'], port=v['port']
            ) for v in endpoints.values()
        ]

    @property
    def base_url(self):
        """
        get the next endpoint from self.endpoints
        """
        return self._resolve().pop()

    @with_retry_connections()
    def request(self, method, endpoint, **kwargs):
        """
        Proxy to requests.request
        :param method: str formatted http method
        :param endpoint: service endpoint
        :param kwargs: kwargs passed directly to requests.request
        :return:
        """
        kwargs.setdefault('timeout', (1, 30))
        return self.session.request(
            method,
            urljoin(self.base_url, endpoint),
            **kwargs
        )

    def get(self, endpoint, **kwargs):
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('POST', endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request('DELETE', endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request('PUT', endpoint, **kwargs)

    def options(self, endpoint, **kwargs):
        return self.request('OPTIONS', endpoint, **kwargs)

    def head(self, endpoint, **kwargs):
        return self.request('HEAD', endpoint, **kwargs)
