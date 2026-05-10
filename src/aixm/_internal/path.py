# @Time   : 2020-04-02
# @Author : zhangxinhao
import os
import sys
import json
import platform
from pathlib import Path, PureWindowsPath

_system = platform.system().lower()
is_linux = _system == 'linux'
_is_windows = _system == 'windows'
DIR_SPLIT = os.sep
COMPILE_SUFFIX = '.pyd' if _is_windows else '.so'


class _PathObject:
    project_path = None
    data_path = None
    models_path = None
    conf_path = None
    logs_path = None


def _getenv(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def _normalize_path(path):
    return os.path.realpath(os.path.expanduser(path))


def _find_project_path_from_run_file(run_file_path):
    if '\\' in run_file_path:
        run_path = PureWindowsPath(run_file_path)
    else:
        run_path = Path(_normalize_path(run_file_path))
    for parent in run_path.parents:
        if parent.name.lower() == 'src':
            return str(parent.parent)
    return None


def _make_project_info(project_path):
    path_obj = PureWindowsPath(project_path) if '\\' in project_path else Path(project_path)
    project_parts = list(path_obj.parts)
    anchor = path_obj.anchor
    if anchor and project_parts and project_parts[0] == anchor:
        project_parts = project_parts[1:]
    project_parts = [part for part in project_parts if part]
    if len(project_parts) == 0:
        project_name = anchor.rstrip('\\/') or 'project'
        return project_name, project_name
    project_name = project_parts[-1]
    parent_parts = project_parts[:-1]
    if len(parent_parts) == 0:
        project_hash = project_name
    else:
        project_hash = '.'.join(map(lambda x: x[:3], parent_parts)) + '.' + project_name
    return project_name, project_hash


def _read_path_config(project_path):
    env_config_path = _getenv('AIXM_CONFIG_PATH')
    if env_config_path is not None and os.path.isfile(_normalize_path(env_config_path)):
        with open(_normalize_path(env_config_path)) as f:
            return json.load(f)

    config_path = None
    user_config_path = _normalize_path('~/.config/aixm_config.json')
    if os.path.isfile(user_config_path):
        config_path = user_config_path
    appdata_path = os.getenv('APPDATA') if _is_windows else None
    if appdata_path is not None:
        win_config_path = os.path.join(appdata_path, 'aixm', 'aixm_config.json')
        if os.path.isfile(win_config_path):
            config_path = win_config_path
    project_config_path = os.path.join(project_path, 'aixm_config.json')
    if os.path.isfile(project_config_path):
        config_path = project_config_path

    if config_path is None:
        return {}
    with open(config_path) as f:
        return json.load(f)


def __init_path():
    project_path = _getenv('PROJECTPATH', 'AIXM_PROJECT_PATH')
    if project_path is None:
        project_path = _find_project_path_from_run_file(sys.argv[0])
        if project_path is None:
            print('PROJECTPATH, src 目录不存在. 路径初始化失败.')
            return
    project_path = _normalize_path(project_path)
    src_path = os.path.join(project_path, 'src')
    if src_path not in sys.path:
        sys.path.append(src_path)
    _PathObject.project_path = project_path
    _PathObject.data_path = os.path.join(project_path, 'data')
    _PathObject.models_path = os.path.join(project_path, 'models')
    _PathObject.conf_path = os.path.join(project_path, 'conf')
    _PathObject.logs_path = os.path.join(project_path, 'logs')

    _project_name, _project_hash = _make_project_info(project_path)

    def replace_hash(path):
        path = path.replace('<project>', _project_name)
        return path.replace('<project_hash>', _project_hash)

    path_dict = _read_path_config(project_path)

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

    data_path = _getenv('AIXM_DATA_PATH', 'DATA_PATH')
    if data_path is not None:
        _PathObject.data_path = replace_hash(data_path)

    models_path = _getenv('AIXM_MODELS_PATH', 'MODELS_PATH')
    if models_path is not None:
        _PathObject.models_path = replace_hash(models_path)

    conf_path = _getenv('AIXM_CONF_PATH', 'CONF_PATH')
    if conf_path is not None:
        _PathObject.conf_path = replace_hash(conf_path)

    logs_path = _getenv('AIXM_LOGS_PATH', 'LOGS_PATH')
    if logs_path is not None:
        _PathObject.logs_path = replace_hash(logs_path)

    print('PROJECT_PATH=' + _PathObject.project_path)
    print('DATA_PATH=' + _PathObject.data_path)
    print('MODELS_PATH=' + _PathObject.models_path)
    print('CONF_PATH=' + _PathObject.conf_path)
    print('LOGS_PATH=' + _PathObject.logs_path)
    print('*' * 36)


__init_path()


def _require_project_path():
    if _PathObject.project_path is None:
        raise RuntimeError("PROJECTPATH 初始化失败")


def reset_path():
    _require_project_path()
    project_path = _PathObject.project_path
    _PathObject.data_path = os.path.join(project_path, 'data')
    _PathObject.models_path = os.path.join(project_path, 'models')
    _PathObject.conf_path = os.path.join(project_path, 'conf')
    _PathObject.logs_path = os.path.join(project_path, 'logs')


def relative_project_path(*args) -> str:
    _require_project_path()
    return os.path.realpath(os.path.join(_PathObject.project_path, *args))


def relative_data_path(*args) -> str:
    _require_project_path()
    return os.path.realpath(os.path.join(_PathObject.data_path, *args))


def relative_conf_path(*args) -> str:
    _require_project_path()
    return os.path.realpath(os.path.join(_PathObject.conf_path, *args))


def relative_models_path(*args) -> str:
    _require_project_path()
    return os.path.realpath(os.path.join(_PathObject.models_path, *args))


def relative_logs_path(*args) -> str:
    _require_project_path()
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
