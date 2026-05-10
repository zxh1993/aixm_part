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
import time
import threading
import queue


def redis_consumer_sync(task_queue, urls, index, max_queue_size):
    while True:
        try:
            conn = redis_conn(index)
            data = recv_request(conn, urls)
            if data is None:
                time.sleep(0.01)
                continue

            url = data[0][12:].decode("utf-8")
            mq_id, request_data = deserialize_request(data[1], PROTOCOL_PICKLE)
            req = Request(url, mq_id, request_data, index, PROTOCOL_PICKLE)

            while task_queue.qsize() >= max_queue_size:
                time.sleep(0.1)

            task_queue.put(req)
        except Exception as e:
            log().error(f'Redis consumer error: {traceback.format_exc()}')
            time.sleep(5)


def worker(task_queue, worker_id):
    while True:
        try:
            ctx = new_context()
            req = task_queue.get()
            ctx['request'] = req

            try:
                h1, h2, h3 = get_handles(req.url)
                h1()
                resp = []
                if 'stream' in req.url:
                    for v in h2():
                        resp.append(v)
                        req.response_suc(v, 'stream')
                    ctx['response'] = resp
                    req.response_suc(resp, 'stream_stop')
                else:
                    resp = h2()
                    ctx['response'] = resp
                    req.response_suc(resp)
                h3()
            except Exception as e:
                log().error(traceback.format_exc())
                req.response_error(str(e))  # 假设有对应的同步版本
            finally:
                task_queue.task_done()

        except Exception as e:
            log().error(f'Worker {worker_id} error: {traceback.format_exc()}')
            time.sleep(1)


def sync_work(thread_num, index, redis_consumer_count=2, max_queue_size=2000):
    """Main sync work coordinator"""
    url_list = get_urls()
    url_list_str = str(url_list)
    real_urls = get_redis_urls()

    task_queue = queue.Queue(maxsize=max_queue_size)

    # 创建Redis消费者线程
    redis_consumer_threads = []
    for _ in range(redis_consumer_count):
        thread = threading.Thread(
            target=redis_consumer_sync,
            args=(task_queue, real_urls, index, max_queue_size),
            daemon=True
        )
        thread.start()
        redis_consumer_threads.append(thread)

    # 创建工作线程
    worker_threads = []
    for i in range(thread_num):
        thread = threading.Thread(
            target=worker,
            args=(task_queue, i),
            daemon=True
        )
        thread.start()
        worker_threads.append(thread)

    # 状态日志线程
    def status_logger():
        while True:
            log().info(f'Queue size: {task_queue.qsize()}, URLs: {url_list_str}')
            time.sleep(30)

    logger_thread = threading.Thread(target=status_logger, daemon=True)
    logger_thread.start()

    # 等待所有线程
    try:
        for thread in redis_consumer_threads + worker_threads + [logger_thread]:
            thread.join()
    except KeyboardInterrupt:
        log().info("Server shutting down gracefully")


def start_queue_server(thread_num=50, index=None, redis_consumer_count=2):
    try:
        sync_work(thread_num, index, redis_consumer_count)
    except KeyboardInterrupt:
        log().info("Server shutting down gracefully")
    except Exception as e:
        log().error(f"Fatal error in sync server: {traceback.format_exc()}")


__all__ = ['start_queue_server']
