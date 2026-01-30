# @Time   : 2019-01-29
# @Author : zhangxinhao
# @Compile : True
import threading


def get_new_func(func, timeout, mutex):
    def decorator(*args, **kwargs):
        if mutex.acquire(timeout=timeout):
            try:
                return func(*args, **kwargs)
            finally:
                mutex.release()
        else:
            raise Exception(func.__name__ + ' acquire timeout')

    return decorator


def lock_class_func(instance, func, mutex_name='', timeout=3):
    mutex_name = '_mutex_' + mutex_name
    if mutex_name in dir(instance):
        mutex = instance.__getattribute__(mutex_name)
    else:
        mutex = threading.Lock()
        instance.__setattr__(mutex_name, mutex)
    new_func = get_new_func(func, timeout, mutex)
    instance.__setattr__(func.__name__, new_func)


def lock_func(mutex=None, timeout=3):
    def decorator_func(func):
        if mutex is None:
            func.mutex = threading.Lock()
        else:
            func.mutex = mutex
        new_func = get_new_func(func, timeout, func.mutex)
        return new_func

    return decorator_func


__all__ = ['lock_class_func', 'lock_func']
