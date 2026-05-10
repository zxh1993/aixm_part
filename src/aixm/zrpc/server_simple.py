# @Time   : 2025-06-30
# @Author : zhangxinhao
# @Compile : True
from aixm.utils import *
from .transfer import *
from .context import new_context
from .route import get_urls, get_redis_urls, get_handles
from .transfer import _recv_request_timeout
from .protocol import *
from .server import Request
import traceback
import time
import threading
from queue import Queue


def work(get_request):
    url_list = get_urls()
    url_list_str = str(url_list)
    real_urls = get_redis_urls()
    while True:
        try:
            ctx = new_context()
            req = get_request(real_urls)
            ctx['request'] = req
            if req is None:
                log().info('FREE:%s' % url_list_str)
                continue
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
                req.response_error(str(e))
        except Exception as e:
            log().error('%s' % traceback.format_exc())
            time.sleep(10)


def start_simple_server(thread_num=1, index=None):
    def get_request(urls):
        conn = redis_conn(index)
        data = recv_request(conn, urls)
        if data is None:
            return None
        url = data[0][12:].decode("utf-8")
        mq_id, data = deserialize_request(data[1], PROTOCOL_PICKLE)
        return Request(url, mq_id, data, index, PROTOCOL_PICKLE)

    if thread_num == 1:
        work(get_request)
    else:
        work_thread_list = list()
        for i in range(thread_num):
            t = threading.Thread(target=work, args=(get_request,))
            work_thread_list.append(t)
            t.start()
        for i in range(thread_num):
            work_thread_list[i].join()


def start_distributed_server(redis_conf_list, thread_num=1):
    data_queue = Queue(1)

    def get_data_from_redis(index):
        redis_conf = redis_conf_list[index]
        conn = redis_conn(redis_conf)
        real_urls = get_redis_urls()
        while True:
            try:
                data = recv_request(conn, real_urls)
                if data is None:
                    continue
                while True:
                    try:
                        data_queue.put((data, redis_conf))
                        break
                    except:
                        log().info('redis index: %d is full' % index)
            except:
                log().error('%s' % traceback.format_exc())
                time.sleep(10)

    def get_request(urls):
        try:
            r = data_queue.get(timeout=_recv_request_timeout * 2 + 1)
            data, redis_conf = r
            url = data[0][12:].decode("utf-8")
            mq_id, data = deserialize_request(data[1], PROTOCOL_PICKLE)
            return Request(url, mq_id, data, redis_conf, PROTOCOL_PICKLE)
        except:
            pass

    redis_num = len(redis_conf_list)
    get_data_thread_list = list()
    for i in range(redis_num):
        t = threading.Thread(target=get_data_from_redis, args=(i,))
        get_data_thread_list.append(t)
        t.daemon = True
        t.start()

    if thread_num == 1:
        work(get_request)
    else:
        work_thread_list = list()
        for i in range(thread_num):
            t = threading.Thread(target=work, args=(get_request,))
            work_thread_list.append(t)
            t.start()
        for i in range(thread_num):
            work_thread_list[i].join()


__all__ = ['start_simple_server', 'start_distributed_server']
