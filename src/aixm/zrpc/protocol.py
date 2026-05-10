# @Time   : 2019-12-03
# @Author : zhangxinhao
# @Compile : True
import pickle

PROTOCOL_PICKLE = 'PICKLE'


def check_protocol(protocol):
    if protocol != PROTOCOL_PICKLE:
        raise Exception('protocol: %s is not exist!' % protocol)


def serialize_request(mq_id, request, protocol):
    check_protocol(protocol)
    data = dict()
    data['data'] = request
    data['mq_id'] = mq_id
    data = pickle.dumps(data)
    return data


def deserialize_request(data, protocol):
    check_protocol(protocol)
    request = pickle.loads(data)
    return request['mq_id'], request['data']


def serialize_result(code, msg, result, protocol):
    check_protocol(protocol)
    data = {
        'code': code,
        'data': result,
        'msg': msg
    }
    return pickle.dumps(data)


def deserialize_result(data, protocol):
    check_protocol(protocol)
    r = pickle.loads(data[1])
    if r['code'] != 0:
        raise Exception(r['msg'])
    if r['msg'] != '':
        return r
    return r['data']


__all__ = ['check_protocol', 'PROTOCOL_PICKLE', 'serialize_request', 'serialize_result',
           'deserialize_request', 'deserialize_result']
