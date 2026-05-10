# @Time   : 2019-06-21
# @Author : zhangxinhao
# @Compile : True
from aixm.utils import *
from .transfer import *
from .context import new_context
from .route import get_urls, get_redis_urls, get_handles
from .protocol import *
from .transfer import _recv_request_timeout
from queue import Queue
import traceback
import time
import asyncio
import threading
import typing


def initialize(*args, **kwargs):
    def decorator(cls):
        return cls(*args, **kwargs)

    return decorator


class Request:
    def __init__(self, url, mq_id, data, index, result_protocol):
        self._url = url
        self._data = data
        self._mq_id = mq_id
        self._index = index
        self._result_protocol = result_protocol

    @property
    def url(self) -> str:
        return self._url

    @property
    def data(self) -> typing.Any:
        return self._data

    @property
    def mq_id(self) -> str:
        return self._mq_id

    @property
    def index(self):
        return self._index

    @property
    def result_protocol(self) -> str:
        return self._result_protocol

    def response_suc(self, result, msg=''):
        data = serialize_result(0, msg, result, self.result_protocol)
        send_result(redis_conn(self.index), self.mq_id, data)

    def response_error(self, error_info):
        data = serialize_result(1, error_info, "", self.result_protocol)
        send_result(redis_conn(self.index), self.mq_id, data)

    async def response_suc_async(self, result, msg=''):
        data = serialize_result(0, msg, result, self.result_protocol)
        await send_result_async(await redis_conn_async(self.index), self.mq_id, data)

    async def response_error_async(self, error_info):
        data = serialize_result(1, error_info, "", self.result_protocol)
        await send_result_async(await redis_conn_async(self.index), self.mq_id, data)


__all__ = ['Request', 'initialize']
