# @Time   : 2019-05-21
# @Author : zhangxinhao
import typing


def get_dict_from_dict(obj, key) -> dict:
    v = obj.get(key)
    if v is None:
        v = dict()
        obj[key] = v
    return v


def get_list_from_dict(obj, key) -> list:
    v = obj.get(key)
    if v is None:
        v = list()
        obj[key] = v
    return v


def get_any_from_dict(obj, key, creator) -> typing.Any:
    v = obj.get(key)
    if v is None:
        v = creator()
        obj[key] = v
    return v


__all__ = ['get_dict_from_dict', 'get_list_from_dict', 'get_any_from_dict']
