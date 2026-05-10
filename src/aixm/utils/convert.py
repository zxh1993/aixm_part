# @Time   : 2018-9-10
# @Author : zhangxinhao
# @Compile : True


def _is_numpy_value(value):
    return type(value).__module__.split('.')[0] == 'numpy'


def _is_numpy_array(value):
    shape = getattr(value, 'shape', None)
    return _is_numpy_value(value) and shape is not None and len(shape) > 0 and hasattr(value, 'tolist')


def _numpy_to_python(value):
    if hasattr(value, 'tolist'):
        return value.tolist()
    raise Exception(str(type(value)) + '不支持的类型')


def _to_json_value(value):
    if _is_numpy_value(value):
        return _numpy_to_python(value)
    type_val = type(value)
    if (type_val == list) or (type_val == tuple):
        return to_jsonlist(value)
    if type_val == dict:
        return to_jsondict(value)
    return value


def _type_name(value):
    type_ = type(value)
    module = type_.__module__
    if module == 'builtins':
        return type_.__name__
    return module + '.' + type_.__name__


def _to_abstract_json_value(value):
    if _is_numpy_array(value):
        return '<numpy.ndarray' + str(value.shape) + '>'
    if _is_numpy_value(value):
        return _numpy_to_python(value)
    type_val = type(value)
    if type_val == str:
        lenv = len(value)
        if lenv > 20:
            return '<char[%d]>' % lenv
        return value
    if (type_val == list) or (type_val == tuple):
        lenv = len(value)
        if lenv > 20:
            type_name = _type_name(value[0]) if lenv > 0 else 'object'
            return '<%s[%d]>' % (type_name, lenv)
        return to_abstract_jsonlist(value)
    if type_val == dict:
        return to_abstract_jsondict(value)
    return value


def to_jsonobj(data) -> dict:
    type_val = type(data)
    type_str = str(type_val)
    if _is_numpy_value(data):
        data = _numpy_to_python(data)
        type_val = type(data)
    if type_val == list:
        data = to_jsonlist(data)
    elif type_val == dict:
        data = to_jsondict(data)
    else:
        raise Exception(type_str + '不支持的类型')
    return data


def to_jsonlist(l) -> list:
    return [_to_json_value(x) for x in l]


def to_jsondict(d) -> dict:
    ret = dict()
    for k, v in d.items():
        ret[k] = _to_json_value(v)
    return ret


def to_abstract_jsonlist(l) -> list:
    return [_to_abstract_json_value(x) for x in l]


def to_abstract_jsondict(d) -> dict:
    ret = dict()
    for k, v in d.items():
        ret[k] = _to_abstract_json_value(v)
    return ret


__all__ = ['to_jsonobj', 'to_abstract_jsondict', 'to_abstract_jsonlist']
