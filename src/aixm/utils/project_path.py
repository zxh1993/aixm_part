# @Time   : 2020-04-02
# @Author : zhangxinhao
import os
import sys
import json
import platform

is_linux = platform.system().lower() == 'linux'
DIR_SPLIT = '/' if is_linux else '\\'
COMPILE_SUFFIX = '.so' if is_linux else '.pyd'


class _PathObject:
    project_path = None
    data_path = None
    models_path = None
    conf_path = None
    logs_path = None


def __init_path():
    project_path = os.getenv('PROJECTPATH')
    if project_path is None:
        file_path = os.path.realpath(sys.argv[0])
        index = file_path.find(f'{DIR_SPLIT}src{DIR_SPLIT}')
        if index == -1:
            print('PROJECTPATH, src 目录不存在. 路径初始化失败.')
            return
        project_path = file_path[:index]
    sys.path.append(os.path.join(project_path, 'src'))
    _PathObject.project_path = project_path
    _PathObject.data_path = os.path.join(project_path, 'data')
    _PathObject.models_path = os.path.join(project_path, 'models')
    _PathObject.conf_path = os.path.join(project_path, 'conf')
    _PathObject.logs_path = os.path.join(project_path, 'logs')

    _splits = project_path.split(DIR_SPLIT)
    _project_name = _splits[-1]
    _splits.pop(-1)
    if _splits[0] == '':
        _splits.pop(0)
    _project_hash = '.'.join(map(lambda x: x[:3], _splits)) + '.' + _project_name

    def replace_hash(path):
        path = path.replace('<project>', _project_name)
        return path.replace('<project_hash>', _project_hash)

    config_path = None
    if is_linux:
        if os.path.isfile(os.path.expanduser('~/.config/aixm_config.json')):
            config_path = os.path.expanduser('~/.config/aixm_config.json')
    if os.path.isfile(os.path.join(project_path, 'aixm_config.json')):
        config_path = os.path.join(project_path, 'aixm_config.json')

    if config_path is not None:
        with open(config_path) as f:
            path_dict = json.load(f)

            data_path = path_dict.get('data_path')
            if data_path is not None:
                _PathObject.data_path = replace_hash(data_path)

            models_path = path_dict.get('models_path')
            if models_path is not None:
                _PathObject.models_path = replace_hash(models_path)

            conf_path = path_dict.get('conf_path')
            if conf_path is not None:
                _PathObject.conf_path = replace_hash(conf_path)

            logs_path = path_dict.get('logs_path')
            if logs_path is not None:
                _PathObject.logs_path = replace_hash(logs_path)

    print('PROJECT_PATH=' + _PathObject.project_path)
    print('DATA_PATH=' + _PathObject.data_path)
    print('MODELS_PATH=' + _PathObject.models_path)
    print('CONF_PATH=' + _PathObject.conf_path)
    print('LOGS_PATH=' + _PathObject.logs_path)
    print('*' * 36)


__init_path()


def reset_path():
    project_path = _PathObject.project_path
    _PathObject.data_path = os.path.join(project_path, 'data')
    _PathObject.models_path = os.path.join(project_path, 'models')
    _PathObject.conf_path = os.path.join(project_path, 'conf')
    _PathObject.logs_path = os.path.join(project_path, 'logs')


def relative_project_path(*args) -> str:
    assert _PathObject.project_path is not None, "PROJECTPATH 初始化失败"
    return os.path.realpath(os.path.join(_PathObject.project_path, *args))


def relative_data_path(*args) -> str:
    assert _PathObject.project_path is not None, "PROJECTPATH 初始化失败"
    return os.path.realpath(os.path.join(_PathObject.data_path, *args))


def relative_conf_path(*args) -> str:
    assert _PathObject.project_path is not None, "PROJECTPATH 初始化失败"
    return os.path.realpath(os.path.join(_PathObject.conf_path, *args))


def relative_models_path(*args) -> str:
    assert _PathObject.project_path is not None, "PROJECTPATH 初始化失败"
    return os.path.realpath(os.path.join(_PathObject.models_path, *args))


def relative_logs_path(*args) -> str:
    assert _PathObject.project_path is not None, "PROJECTPATH 初始化失败"
    return os.path.realpath(os.path.join(_PathObject.logs_path, *args))


_config_dict = dict()


def local_config(config_name='config.json') -> dict:
    config = _config_dict.get(config_name)
    if config is None:
        with open(relative_conf_path(config_name)) as f:
            config = json.load(f)
            _config_dict[config_name] = config
    if config is None:
        raise Exception('config.json is not exist!')
    return config


def set_local_config(config_name, config):
    _config_dict[config_name] = config


__all__ = ['reset_path',
           'relative_project_path',
           'relative_data_path',
           'relative_conf_path',
           'relative_models_path',
           'relative_logs_path',
           'local_config',
           'set_local_config',
           'is_linux',
           'DIR_SPLIT',
           'COMPILE_SUFFIX']
