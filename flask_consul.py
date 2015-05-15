import yaml
import os
import consulate

DEFAULT_KV_NAMESPACE = "config/{service}/{environment}".format(
    service=os.environ.get('SERVICE', 'generic_service'),
    environment=os.environ.get('ENVIRONMENT', 'generic_environment')
)

class Consul(object):
    """
    The Consul flask.ext object is responsible for connecting and querying
    consul (using gmr/consulate).
    """

    def __init__(self, app=None, **kwargs):
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

        h = self.kwargs.get('consul_host') or \
            os.environ.get('CONSUL_HOST', 'localhost')
        self.session = consulate.Session(host=h)

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
            # Use yaml.load() instead of json.loads() since we want want to
            # load non-strict json
            self.app.config[k] = yaml.load(v)
            self.app.logger.debug(
                "Set {k}={v} from consul kv '{ns}'".format(
                    k=k,
                    v=v,
                    ns=namespace,)
            )