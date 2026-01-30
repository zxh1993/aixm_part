# @Time   : 2019-09-23
# @Author : zhangxinhao
# @Compile : True
import os
import typing


def search_filepaths(root_path, file_filter) -> list:
    r = list()
    for parent, dirs, files in os.walk(root_path):
        for file in files:
            path = os.path.join(parent, file)
            if file_filter(path):
                r.append(path)
    return r


def parse_filepath_prefix(filepath) -> str:
    name = parse_filepath_name(filepath)
    return name.split('.')[0]


def parse_filepath_suffix(filepath) -> str:
    return filepath.split('.')[1]


def parse_filepath_name(filepath) -> str:
    return os.path.split(filepath)[1]


def parse_filepath_parent_name(filepath) -> str:
    return os.path.basename(os.path.dirname(filepath))


def parse_filepath_dir(filepath) -> str:
    return os.path.split(filepath)[0]


def replace_filepath_suffix(filepath, new_suffix) -> str:
    return filepath.split('.')[0] + '.' + new_suffix


def split_filepath(filepath) -> typing.Tuple[typing.AnyStr, typing.AnyStr]:
    return os.path.split(filepath)


__all__ = ['search_filepaths', 'parse_filepath_prefix', 'parse_filepath_suffix', 'parse_filepath_name',
           'parse_filepath_parent_name', 'parse_filepath_dir', 'replace_filepath_suffix', 'split_filepath']
