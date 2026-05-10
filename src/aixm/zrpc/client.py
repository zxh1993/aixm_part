# @Time   : 2019-06-21
# @Author : zhangxinhao
# @Compile : True
from aixm.utils.local_redis import *
from .transfer import *
from .protocol import *
import typing


class Response:
    def __init__(self, mq_id, data, index, result_protocol):
        self._data = data
        self._mq_id = mq_id
        self._index = index
        self._result_protocol = result_protocol

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

    def get(self, timeout=None, interval=0) -> typing.Any:
        data = recv_result_polling(redis_conn(self.index), self.mq_id, timeout, interval)
        if data is None:
            raise Exception('MqResponse pop timeout')
        return deserialize_result(data, self.result_protocol)

    def stream(self, timeout=None, interval=0) -> typing.Iterable[typing.Any]:
        conn = redis_conn(self.index)
        while True:
            data = recv_result_polling(conn, self.mq_id, timeout, interval)
            if data is None:
                raise Exception('MqResponse pop timeout')
            r = deserialize_result(data, self.result_protocol)
            data, msg = r['data'], r['msg']
            if msg != 'stream':
                break
            yield data

    async def get_async(self, timeout=None, interval=0) -> typing.Any:
        data = await recv_result_polling_async(await redis_conn_async(self.index), self.mq_id, timeout, interval)
        if data is None:
            raise Exception('MqResponse pop timeout')
        return deserialize_result(data, self.result_protocol)

    async def stream_async(self, timeout=None, interval=0) -> typing.AsyncGenerator[typing.Any, None]:
        conn = await redis_conn_async(self.index)
        while True:
            data = await recv_result_polling_async(conn, self.mq_id, timeout, interval)
            if data is None:
                raise Exception('MqResponse pop timeout')
            r = deserialize_result(data, self.result_protocol)
            data, msg = r['data'], r['msg']
            if msg != 'stream':
                break
            yield data


def invoke(url, request, index=None) -> Response:
    conn = redis_conn(index)
    mq_id = get_mq_id(conn)
    data = serialize_request(mq_id, request, PROTOCOL_PICKLE)
    send_request(conn, 'AIXM_MQ_URL_' + url, data)
    return Response(mq_id, data, index, PROTOCOL_PICKLE)


async def invoke_async(url, request, index=None) -> Response:
    conn = await redis_conn_async(index)
    mq_id = await get_mq_id_async(conn)
    data = serialize_request(mq_id, request, PROTOCOL_PICKLE)
    await send_request_async(conn, 'AIXM_MQ_URL_' + url, data)
    return Response(mq_id, data, index, PROTOCOL_PICKLE)


async def invoke_get_async(url, request, index=None, timeout=None, interval=0) -> typing.Any:
    conn = await redis_conn_async(index)
    mq_id = await get_mq_id_async(conn)
    data = serialize_request(mq_id, request, PROTOCOL_PICKLE)
    await send_request_async(conn, 'AIXM_MQ_URL_' + url, data)
    return await Response(mq_id, data, index, PROTOCOL_PICKLE).get_async(timeout, interval)


__all__ = ['Response', 'invoke', 'invoke_async', 'invoke_get_async']
