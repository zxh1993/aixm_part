# @Time   : 2018-12-26
# @Author : zhangxinhao
# @Compile : True
import os
from .project_path import relative_conf_path
import asyncio
import redis
import json
import threading
import redis.asyncio

__pool_dict = dict()

__pool_dict_async = dict()

_async_lock = asyncio.Lock()

_socket_timeout = 100
_mutex = threading.Lock()


def get_redis_socket_timeout() -> int:
    return _socket_timeout


def set_redis_socket_timeout(socket_timeout):
    global _socket_timeout
    _socket_timeout = socket_timeout


__redis_conf = {
    "host": os.getenv('REDIS_HOST', "127.0.0.1"),
    "port": int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD')
}
try:
    with open(relative_conf_path('redis.json'), encoding='UTF-8') as f:
        __redis_conf = json.load(f)
except:
    pass


def redis_conn_key(index):
    redis_conf = index
    if redis_conf is None:
        redis_conf = __redis_conf
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


def redis_conn_real_host(index) -> str:
    redis_conf = index
    if redis_conf is None:
        redis_conf = __redis_conf
    host = redis_conf.get('host')
    if host is None:
        host = '127.0.0.1'
    return host


def redis_conn(index=None) -> redis.Redis:
    redis_conf = index
    key, redis_conf = redis_conn_key(redis_conf)
    conn = __pool_dict.get(key)
    if conn is None:
        with _mutex:
            conn = __pool_dict.get(key)
            if conn is None:
                if 'max_connections' in redis_conf:
                    pool = redis.BlockingConnectionPool(**__redis_conf)
                else:
                    pool = redis.ConnectionPool(**redis_conf)
                conn = redis.Redis(connection_pool=pool)
                __pool_dict[key] = conn
    return conn


async def redis_conn_async(index=None) -> redis.asyncio.Redis:
    redis_conf = index
    key, redis_conf = redis_conn_key(redis_conf)
    conn = __pool_dict_async.get(key)
    if conn is None:
        async with _async_lock:
            conn = __pool_dict_async.get(key)
            if conn is None:
                if 'max_connections' in redis_conf:
                    pool = redis.asyncio.BlockingConnectionPool(**redis_conf)
                else:
                    pool = redis.asyncio.ConnectionPool(**redis_conf)
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
