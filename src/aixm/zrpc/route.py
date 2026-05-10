# @Time   : 2019-06-21
# @Author : zhangxinhao
# @Compile : True
from aixm.utils import *
from .context import *

_route_dict = dict()

PHASE_BEFORE = "BEFORE"
PHASE_DURING = "DURING"
PHASE_AFTER = "AFTER"


def default_before_handle():
    log().info('RECV,%s,%s' % (request.mq_id[13:], request.url))


def default_during_handle():
    return "ok"


def default_after_handle():
    log().info('SEND,%s,%s' % (request.mq_id[13:], request.url))


def response_route(url, phase=PHASE_DURING):
    def decorator(func):
        add_response_route(url, func, phase)
        return func

    return decorator


def add_response_route(url, func, phase=PHASE_DURING):
    handles = _route_dict.get(url)
    if handles is None:
        _route_dict[url] = {
            phase: func
        }
    else:
        if handles.get(phase) is not None:
            raise Exception("%s %s is exist!" % (url, phase))
        handles[phase] = func


def get_handles(url):
    handles = _route_dict[url]
    return \
        (get_any_from_dict(handles, PHASE_BEFORE, lambda: default_before_handle),
         get_any_from_dict(handles, PHASE_DURING, lambda: default_during_handle),
         get_any_from_dict(handles, PHASE_AFTER, lambda: default_after_handle))


def get_urls():
    return list(_route_dict.keys())


def get_redis_urls():
    url_list = list(_route_dict.keys())
    return ['AIXM_MQ_URL_' + url for url in url_list]


'''
#copy-begin
PHASE_BEFORE = "BEFORE"
PHASE_DURING = "DURING"
PHASE_AFTER = "AFTER"
#copy-end
'''

__all__ = ['PHASE_BEFORE', 'PHASE_DURING', 'PHASE_AFTER', 'response_route', 'add_response_route']
