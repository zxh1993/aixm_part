# @Time   : 2018-12-26
# @Author : zhangxinhao
from aixm._internal.path import relative_conf_path
import asyncio
import os
import redis
import json
import threading
import redis.asyncio

__pool_dict = dict()

__pool_dict_async = dict()

_async_lock = asyncio.Lock()

_socket_timeout = 100
_mutex = threading.Lock()


def _getenv(*names):
    for name in names:
        value = os.getenv(name)
        if value is not None and value != '':
            return value
    return None


def _getenv_int(*names):
    value = _getenv(*names)
    if value is None:
        return None
    return _parse_int(value, '/'.join(names))


def _parse_int(value, name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError('%s must be an integer, got %r' % (name, value))


def _normalize_redis_conf(redis_conf):
    for name in ('port', 'db', 'max_connections'):
        value = redis_conf.get(name)
        if value is not None:
            redis_conf[name] = _parse_int(value, 'redis_conf.%s' % name)
    return redis_conf


def _make_pool_conf(redis_conf):
    pool_conf = dict(redis_conf)
    if pool_conf.get('host') is None:
        pool_conf['host'] = '127.0.0.1'
    if pool_conf.get('port') is None:
        pool_conf['port'] = 6379
    if pool_conf.get('db') is None:
        pool_conf['db'] = 0
    if _socket_timeout is not None:
        pool_conf.setdefault('socket_timeout', _socket_timeout)
        pool_conf.setdefault('socket_connect_timeout', _socket_timeout)
    return pool_conf


def _load_redis_conf():
    redis_conf = {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0
    }
    try:
        config_path = relative_conf_path('redis.json')
    except RuntimeError:
        config_path = None
    if config_path is not None and os.path.isfile(config_path):
        with open(config_path, encoding='UTF-8') as f:
            config = json.load(f)
        if not isinstance(config, dict):
            raise TypeError('redis.json must contain a JSON object')
        redis_conf.update(config)

    env_value = _getenv('AIXM_REDIS_HOST', 'REDIS_HOST')
    if env_value is not None:
        redis_conf['host'] = env_value

    env_value = _getenv_int('AIXM_REDIS_PORT', 'REDIS_PORT')
    if env_value is not None:
        redis_conf['port'] = env_value

    env_value = _getenv_int('AIXM_REDIS_DB', 'REDIS_DB')
    if env_value is not None:
        redis_conf['db'] = env_value

    env_value = _getenv('AIXM_REDIS_PASSWORD', 'REDIS_PASSWORD')
    if env_value is not None:
        redis_conf['password'] = env_value

    env_value = _getenv('AIXM_REDIS_USERNAME', 'REDIS_USERNAME')
    if env_value is not None:
        redis_conf['username'] = env_value

    env_value = _getenv_int('AIXM_REDIS_MAX_CONNECTIONS', 'REDIS_MAX_CONNECTIONS')
    if env_value is not None:
        redis_conf['max_connections'] = env_value

    return _normalize_redis_conf(redis_conf)


def get_redis_socket_timeout() -> int:
    return _socket_timeout


def set_redis_socket_timeout(socket_timeout):
    global _socket_timeout
    _socket_timeout = socket_timeout


__redis_conf = _load_redis_conf()


def _get_redis_conf(redis_conf=None, kwargs=None):
    if kwargs is None:
        kwargs = {}
    if 'index' in kwargs:
        if redis_conf is not None:
            raise TypeError('redis_conf and index cannot both be set')
        redis_conf = kwargs.pop('index')
    if len(kwargs) > 0:
        raise TypeError('unexpected keyword argument: %s' % next(iter(kwargs)))
    if redis_conf is None:
        redis_conf = __redis_conf
    if not hasattr(redis_conf, 'get'):
        raise TypeError('redis_conf must be a dict-like object or None')
    return _normalize_redis_conf(redis_conf)


def redis_conn_key(redis_conf=None, **kwargs):
    redis_conf = _get_redis_conf(redis_conf, kwargs)
    host = redis_conf.get('host')
    port = redis_conf.get('port')
    db = redis_conf.get('db')
    if host is None:
        host = '127.0.0.1'
    if port is None:
        port = 6379
    if db is None:
        db = 0
    key = "%s-%d-%d" % (host, port, db)
    return key, redis_conf


def redis_conn_real_host(redis_conf=None, **kwargs) -> str:
    redis_conf = _get_redis_conf(redis_conf, kwargs)
    host = redis_conf.get('host')
    if host is None:
        host = '127.0.0.1'
    return host


def redis_conn(redis_conf=None, **kwargs) -> redis.Redis:
    redis_conf = _get_redis_conf(redis_conf, kwargs)
    key, redis_conf = redis_conn_key(redis_conf)
    conn = __pool_dict.get(key)
    if conn is None:
        with _mutex:
            conn = __pool_dict.get(key)
            if conn is None:
                pool_conf = _make_pool_conf(redis_conf)
                if 'max_connections' in pool_conf or 'timeout' in pool_conf:
                    pool = redis.BlockingConnectionPool(**pool_conf)
                else:
                    pool = redis.ConnectionPool(**pool_conf)
                conn = redis.Redis(connection_pool=pool)
                __pool_dict[key] = conn
    return conn


async def redis_conn_async(redis_conf=None, **kwargs) -> redis.asyncio.Redis:
    redis_conf = _get_redis_conf(redis_conf, kwargs)
    key, redis_conf = redis_conn_key(redis_conf)
    conn = __pool_dict_async.get(key)
    if conn is None:
        async with _async_lock:
            conn = __pool_dict_async.get(key)
            if conn is None:
                pool_conf = _make_pool_conf(redis_conf)
                if 'max_connections' in pool_conf or 'timeout' in pool_conf:
                    pool = redis.asyncio.BlockingConnectionPool(**pool_conf)
                else:
                    pool = redis.asyncio.ConnectionPool(**pool_conf)
                conn = redis.asyncio.Redis(connection_pool=pool)
                __pool_dict_async[key] = conn
    return conn


'''
#copy-begin
import redis
import redis.asyncio
#copy-end
'''

__all__ = ['redis_conn', 'redis_conn_async', 'get_redis_socket_timeout', 'set_redis_socket_timeout',
           'redis_conn_real_host', 'redis_conn_key']
