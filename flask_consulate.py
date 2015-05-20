import yaml
import os
import consulate
import time
from requests.exceptions import ConnectionError

DEFAULT_KV_NAMESPACE = "config/{service}/{environment}/".format(
    service=os.environ.get('SERVICE', 'generic_service'),
    environment=os.environ.get('ENVIRONMENT', 'generic_environment')
)

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
                except ConnectionError:
                    tries += 1
                    if tries >= max_tries:
                        raise ConsulConnectionError
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
            namespace = DEFAULT_KV_NAMESPACE
        for k, v in self.session.kv.find(namespace).iteritems():
            k = k.replace(namespace, '')
            self.app.config[k] = v
            msg = "Set {k}={v} from consul kv '{ns}'".format(
                k=k,
                v=v,
                ns=namespace,
            )
            self.app.logger.debug(msg)
