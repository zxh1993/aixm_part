# @Time   : 2019-11-29
# @Author : zhangxinhao
# @Compile : True
import time
import asyncio

DEFAULT_RECV_REQ_TIMEOUT = 60
_recv_request_timeout = DEFAULT_RECV_REQ_TIMEOUT
DEFAULT_SEND_RES_TIMEOUT = 75
_send_result_timeout = DEFAULT_SEND_RES_TIMEOUT
DEFAULT_SEND_REQ_TIMEOUT = 90
_send_request_timeout = DEFAULT_SEND_REQ_TIMEOUT
DEFAULT_RECV_RES_TIMEOUT = 60
_recv_result_timeout = DEFAULT_RECV_RES_TIMEOUT
MAX_ID = max(DEFAULT_SEND_RES_TIMEOUT, DEFAULT_SEND_REQ_TIMEOUT) * 200000

_get_mq_id_sha = None
_get_mq_id_f = '''
local id = redis.pcall("incr", "{key}")
local t = type(id)
if (t ~= "number") then
  id = 0
  redis.call("set", "{key}", 0)
end
if (id >= {max_id})
then
  id = 0
  redis.call("set", "{key}", 0)
end
return tostring(id)
'''


def get_mq_id(conn):
    global _get_mq_id_sha
    if _get_mq_id_sha is None:
        script = _get_mq_id_f.format(key='AIXM_MQ_ID', max_id=MAX_ID)
        _get_mq_id_sha = conn.script_load(script)
    try:
        return 'AIXM_MQ_RESP_' + conn.evalsha(_get_mq_id_sha, 0).decode()
    except Exception:
        script = _get_mq_id_f.format(key='AIXM_MQ_ID', max_id=MAX_ID)
        _get_mq_id_sha = conn.script_load(script)
        return 'AIXM_MQ_RESP_' + conn.evalsha(_get_mq_id_sha, 0).decode()


async def get_mq_id_async(conn):
    global _get_mq_id_sha
    if _get_mq_id_sha is None:
        script = _get_mq_id_f.format(key='AIXM_MQ_ID', max_id=MAX_ID)
        _get_mq_id_sha = await conn.script_load(script)
    try:
        return 'AIXM_MQ_RESP_' + (await conn.evalsha(_get_mq_id_sha, 0)).decode()
    except Exception:
        script = _get_mq_id_f.format(key='AIXM_MQ_ID', max_id=MAX_ID)
        _get_mq_id_sha = await conn.script_load(script)
        return 'AIXM_MQ_RESP_' + (await conn.evalsha(_get_mq_id_sha, 0)).decode()


_lpush_sha = None
_lpush_max_size = 1000
_lpush_f = '''
local url = KEYS[1]
local max_size = tonumber(ARGV[2])
local expire_time = tonumber(ARGV[3])
local l = redis.pcall("llen", url)
local t = type(l)
if (t ~= "number") then
  redis.call("del", url)
  l = 0
end
if (l >= max_size) then
  return -1
end
redis.call("lpush", url, ARGV[1])
redis.call("expire", url, expire_time)
return l+1
'''


def _lpush_expire(conn, key, data, timeout):
    global _lpush_sha
    if _lpush_sha is None:
        _lpush_sha = conn.script_load(_lpush_f)
    try:
        return conn.evalsha(_lpush_sha, 1, key, data, _lpush_max_size, timeout)
    except Exception:
        flag = conn.script_exists(_lpush_sha)[0]
        if not flag:
            _lpush_sha = conn.script_load(_lpush_f)
            return conn.evalsha(_lpush_sha, 1, key, data, _lpush_max_size, timeout)
        raise


async def _lpush_expire_async(conn, key, data, timeout):
    global _lpush_sha
    if _lpush_sha is None:
        _lpush_sha = await conn.script_load(_lpush_f)
    try:
        return await conn.evalsha(_lpush_sha, 1, key, data, _lpush_max_size, timeout)
    except Exception:
        flag = (await conn.script_exists(_lpush_sha))[0]
        if not flag:
            _lpush_sha = await conn.script_load(_lpush_f)
            return await conn.evalsha(_lpush_sha, 1, key, data, _lpush_max_size, timeout)
        raise


def set_recv_request_timeout(t):
    global _recv_request_timeout
    _recv_request_timeout = t


def set_send_result_timeout(t):
    global _send_result_timeout
    _send_result_timeout = t


def set_send_request_timeout(t):
    global _send_request_timeout
    _send_request_timeout = t


def set_recv_result_timeout(t):
    global _recv_result_timeout
    _recv_result_timeout = t


def resolve_recv_result_timeout(timeout):
    if timeout is None:
        return _recv_result_timeout
    return timeout


def recv_request(conn, urls):
    return conn.brpop(urls, _recv_request_timeout)


async def recv_request_async(conn, urls):
    return await conn.brpop(urls, _recv_request_timeout)


def send_result(conn, id_, data):
    _lpush_expire(conn, id_, data, _send_result_timeout)


async def send_result_async(conn, id_, data):
    await _lpush_expire_async(conn, id_, data, _send_result_timeout)


def send_request(conn, url, data):
    _lpush_expire(conn, url, data, _send_request_timeout)


async def send_request_async(conn, url, data):
    await _lpush_expire_async(conn, url, data, _send_request_timeout)


def recv_result(conn, id_, timeout=None):
    timeout = resolve_recv_result_timeout(timeout)
    return conn.brpop(id_, timeout)


async def recv_result_async(conn, id_, timeout=None):
    timeout = resolve_recv_result_timeout(timeout)
    return await conn.brpop(id_, timeout)


def recv_result_polling(conn, id_, timeout=None, interval=0):
    timeout = resolve_recv_result_timeout(timeout)
    if abs(interval) < 0.01:
        return recv_result(conn, id_, timeout)
    num = int(timeout / interval) + 1
    for i in range(num):
        time.sleep(interval)
        r = conn.rpop(id_)
        if r is not None:
            return (id_, r)
    return None


async def recv_result_polling_async(conn, id_, timeout=None, interval=0):
    timeout = resolve_recv_result_timeout(timeout)
    if abs(interval) < 0.01:
        return await recv_result_async(conn, id_, timeout)
    num = int(timeout / interval) + 1
    for i in range(num):
        await asyncio.sleep(interval)
        r = await conn.rpop(id_)
        if r is not None:
            return (id_, r)
    return None
