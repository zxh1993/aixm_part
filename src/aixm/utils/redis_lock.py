# @Time   : 2020-12-20
# @Author : zhangxinhao
# @Compile : True
import time
import uuid
import asyncio
from .local_redis import redis_conn, redis_conn_async

_unlock_script = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""


class RedisLock:
    def __init__(self, lock_name, redis_conf=None, acquire_timeout=12, lock_timeout=None):
        self.redis_conf = redis_conf
        self.lock_name = 'AIXM_RDLOCK' + str(lock_name)
        self.acquire_timeout = int(acquire_timeout)
        if lock_timeout is None:
            self.lock_timeout = self.acquire_timeout
        else:
            self.lock_timeout = int(lock_timeout)
        self.lock_timeout = max(self.lock_timeout, 2)
        # 最多锁180秒，超出就是逻辑问题
        self.lock_timeout = min(self.lock_timeout, 180)
        self.uuid = None

    def __enter__(self):
        self.uuid = str(uuid.uuid4())
        lock_end_time = time.time() + self.acquire_timeout
        while time.time() < lock_end_time:
            if redis_conn(self.redis_conf).set(self.lock_name, self.uuid, ex=self.lock_timeout, nx=True):
                return
            time.sleep(0.01)
        self.uuid = None
        raise Exception("RedisLock acquire_timeout")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.uuid is None:
            return
        unlock = redis_conn(self.redis_conf).register_script(_unlock_script)
        unlock(keys=[self.lock_name], args=[self.uuid])


class RedisLockAsync:
    def __init__(self, lock_name, redis_conf=None, acquire_timeout=12, lock_timeout=None):
        self.redis_conf = redis_conf
        self.lock_name = 'AIXM_RDLOCK' + str(lock_name)
        self.acquire_timeout = int(acquire_timeout)
        if lock_timeout is None:
            self.lock_timeout = self.acquire_timeout
        else:
            self.lock_timeout = int(lock_timeout)
        self.lock_timeout = max(self.lock_timeout, 2)
        # 最多锁180秒，超出就是逻辑问题
        self.lock_timeout = min(self.lock_timeout, 180)
        self.uuid = None

    async def __aenter__(self):
        self.uuid = str(uuid.uuid4())
        lock_end_time = time.time() + self.acquire_timeout
        redis_client = await redis_conn_async(self.redis_conf)

        while time.time() < lock_end_time:
            if await redis_client.set(self.lock_name, self.uuid, ex=self.lock_timeout, nx=True):
                return self
            await asyncio.sleep(0.01)

        self.uuid = None
        raise Exception("RedisLockA acquire_timeout")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.uuid is None:
            return

        redis_client = await redis_conn_async(self.redis_conf)
        unlock = redis_client.register_script(_unlock_script)
        await unlock(keys=[self.lock_name], args=[self.uuid])


__all__ = ['RedisLock', 'RedisLockAsync']
