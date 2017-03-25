# coding: utf-8

from requests.exceptions import ConnectionError


class ConsulConnectionError(ConnectionError):
    """
    A connection error related to Consul happened.
    """
    pass
