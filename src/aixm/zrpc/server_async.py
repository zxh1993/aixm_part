# @Time   : 2025-06-30
# @Author : zhangxinhao
# @Compile : True
from aixm.utils import *
from .transfer import *
from .context import new_context
from .route import get_urls, get_redis_urls, get_handles
from .protocol import *
from .server import Request
import traceback
import asyncio


async def redis_consumer_async(task_queue, urls, index, max_queue_size):
    while True:
        try:
            conn = await redis_conn_async(index)
            data = await recv_request_async(conn, urls)
            if data is None:
                await asyncio.sleep(0.01)
                continue

            url = data[0][12:].decode("utf-8")
            mq_id, request_data = deserialize_request(data[1], PROTOCOL_PICKLE)
            req = Request(url, mq_id, request_data, index, PROTOCOL_PICKLE)

            while task_queue.qsize() >= max_queue_size:
                await asyncio.sleep(0.1)

            await task_queue.put(req)
        except Exception as e:
            log().error(f'Redis consumer error: {traceback.format_exc()}')
            await asyncio.sleep(5)


async def worker(task_queue, worker_id):
    while True:
        try:
            ctx = new_context()
            req = await task_queue.get()
            ctx['request'] = req

            try:
                h1, h2, h3 = get_handles(req.url)
                h1()
                resp = []
                if 'stream' in req.url:
                    async for v in h2():
                        resp.append(v)
                        await req.response_suc_async(v, 'stream')
                    ctx['response'] = resp
                    await req.response_suc_async(resp, 'stream_stop')
                else:
                    resp = await h2()
                    ctx['response'] = resp
                    await req.response_suc_async(resp)
                h3()
            except Exception as e:
                log().error(traceback.format_exc())
                await req.response_error_async(str(e))
            finally:
                task_queue.task_done()

        except Exception as e:
            log().error(f'Worker {worker_id} error: {traceback.format_exc()}')
            await asyncio.sleep(1)


async def async_work(coro_num, index, redis_consumer_count=2, max_queue_size=2000):
    """Main async work coordinator"""
    url_list = get_urls()
    url_list_str = str(url_list)
    real_urls = get_redis_urls()

    task_queue = asyncio.Queue(maxsize=max_queue_size)

    redis_consumers = [
        asyncio.create_task(
            redis_consumer_async(task_queue=task_queue,
                                 urls=real_urls, index=index, max_queue_size=max_queue_size)
        )
        for _ in range(redis_consumer_count)
    ]

    workers = [
        asyncio.create_task(worker(task_queue, i))
        for i in range(coro_num)
    ]

    # Log periodically
    async def status_logger():
        while True:
            log().info(f'Queue size: {task_queue.qsize()}, URLs: {url_list_str}')
            await asyncio.sleep(30)

    logger_task = asyncio.create_task(status_logger())
    all_tasks = redis_consumers + workers + [logger_task]
    await asyncio.gather(*all_tasks)


def start_async_server(coro_num=100, index=None, redis_consumer_count=2):
    try:
        asyncio.run(async_work(coro_num, index, redis_consumer_count))
    except KeyboardInterrupt:
        log().info("Server shutting down gracefully")
    except Exception as e:
        log().error(f"Fatal error in async server: {traceback.format_exc()}")


__all__ = ['start_async_server']
