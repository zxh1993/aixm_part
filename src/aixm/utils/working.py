# @Time   : 2019-01-29
# @Author : zhangxinhao
# @Compile : True
import os
import importlib
from aixm._internal.path import relative_project_path, DIR_SPLIT, is_linux
from .logging import log
import typing
import platform

_system = platform.system().lower()
_is_supported_system = is_linux or _system == 'darwin'


def _require_supported_system():
    if not _is_supported_system:
        raise RuntimeError("目前只支持linux和macos")


def kill_other(name, key=None, is_create_new=True):
    _require_supported_system()
    if key is None:
        key = name
    os.makedirs(relative_project_path('logs', 'pid'), exist_ok=True)
    pid_filepath = relative_project_path(relative_project_path('logs', 'pid', name))
    if os.path.isfile(pid_filepath):
        with open(pid_filepath) as f:
            pid = f.readline()
            cmd = 'ps -ef | grep %s | grep %s | grep -v grep' % (key, pid)
            grep_result = os.popen(cmd).readlines()
            log().warning('[cmd] ' + cmd)
            for r in grep_result:
                log().warning('[grep result] ' + r)
            if len(grep_result) > 0:
                os.system('kill -9 %s' % pid)
    with open(pid_filepath, 'w') as f:
        f.write(str(os.getpid()))
    if not is_create_new:
        if os.path.isfile(pid_filepath):
            os.remove(pid_filepath)


def kill_all(key):
    _require_supported_system()
    lines = os.popen('ps -ef | grep %s | grep python | grep -v grep' % key)
    cur_pid = int(os.getpid())
    for line in lines:
        pid = int(line.split()[1])
        if pid != cur_pid:
            os.system("kill -9 %d" % pid)


def run_this(name, *args, **kwargs) -> typing.Callable:
    def run(func):
        if name == '__main__':
            func(*args, **kwargs)

    return run


def get_class_or_func(class_or_func_path) -> typing.Any:
    class_module = class_or_func_path[:class_or_func_path.rfind('.')]
    class_or_func_path = class_or_func_path[class_or_func_path.rfind('.') + 1:]
    return getattr(importlib.import_module(class_module), class_or_func_path)


def collect_modules(root_path, root_package) -> list:
    if not os.path.exists(root_path):
        return []
    if os.path.isfile(root_path):
        if root_path.endswith('.py'):
            root_path = root_path[root_path.rfind(root_package):-3]
            root_path = root_path.replace(DIR_SPLIT, '.')
            return [root_path]
        elif root_path.endswith('.so'):
            index = root_path.rfind(DIR_SPLIT)
            index = root_path.find('.', index)
            root_path = root_path[root_path.rfind(root_package):index]
            root_path = root_path.replace(DIR_SPLIT, '.')
            return [root_path]
        else:
            return []

    if os.path.isdir(root_path):
        r = []
        filenames = os.listdir(root_path)
        for filename in filenames:
            new_path = os.path.join(root_path, filename)
            r += collect_modules(new_path, root_package)
        return r


def find_attributes(root_path, root_package, filter_) -> list:
    ret = list()
    modules = collect_modules(root_path, root_package)
    for module_name in modules:
        mod = importlib.import_module(module_name)
        attributes = dir(mod)
        for attribute_name in attributes:
            attribute = getattr(mod, attribute_name)
            if filter_(module_name, attribute_name, attribute):
                ret.append(attribute)
    return ret


__all__ = ['kill_other', 'kill_all', 'run_this', 'get_class_or_func', 'collect_modules', 'find_attributes']
