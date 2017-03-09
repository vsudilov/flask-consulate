# coding: utf-8

import time
import functools

from requests.exceptions import ConnectionError, ConnectTimeout

from flask_consulate.exceptions import ConsulConnectionError


def with_retry_connections(max_tries=3, sleep=0.05):
    """
    Decorator that wraps an entire function in a try/except clause. On
    requests.exceptions.ConnectionError, will re-run the function code
    until success or max_tries is reached.

    :param max_tries: maximum number of attempts before giving up
    :param sleep: time to sleep between tries, or None
    """
    def decorator(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            tries = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except (ConnectionError, ConnectTimeout) as e:
                    tries += 1
                    if tries >= max_tries:
                        raise ConsulConnectionError(e)
                    if sleep:
                        time.sleep(sleep)
        return f_retry
    return decorator
