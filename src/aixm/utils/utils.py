# @Time   : 2020-04-08
# @Author : zhangxinhao
# @Compile : True
import hashlib
import os
import datetime
import time
import math
import platform
import importlib


def cal_str_md5(s) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def cal_file_md5(filepath) -> str:
    md5file = open(filepath, 'rb')
    md5 = hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    return md5


def get_class_or_func(class_or_func_path):
    class_module = class_or_func_path[:class_or_func_path.rfind('.')]
    class_or_func_path = class_or_func_path[class_or_func_path.rfind('.') + 1:]
    return getattr(importlib.import_module(class_module), class_or_func_path)


def current_time() -> tuple:
    now = datetime.datetime.now()
    ymd = now.strftime('%Y-%m-%d')
    hms = now.strftime('%H:%M:%S')
    return ymd, hms


class TimeNow:
    def __init__(self):
        self._timestamp = time.time()
        self._localtime = time.localtime(self._timestamp)

    def timestamp(self) -> float:
        return self._timestamp

    def _get_localtime(self, timestamp=None):
        if timestamp is None:
            return self._localtime
        return time.localtime(timestamp)

    def ymd(self, timestamp=None) -> str:
        return time.strftime("%Y-%m-%d", self._get_localtime(timestamp))

    def hms(self, timestamp=None) -> str:
        return time.strftime("%H:%M:%S", self._get_localtime(timestamp))

    def ymdhms(self, timestamp=None) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", self._get_localtime(timestamp))

    def ymdhms_strip(self, timestamp=None) -> str:
        return time.strftime("%Y%m%d-%H%M%S", self._get_localtime(timestamp))

    def ymdhmsm(self, timestamp=None) -> str:
        if timestamp is None:
            timestamp = self._timestamp
        ymdhms = self.ymdhms(timestamp)
        ms = int((math.modf(timestamp)[0]) * 1000)
        return "%s.%03d" % (ymdhms, ms)

    def ymdhmsm_strip(self, timestamp=None) -> str:
        if timestamp is None:
            timestamp = self._timestamp
        ymdhms_strip = self.ymdhms_strip(timestamp)
        ms = int((math.modf(timestamp)[0]) * 1000)
        return "%s-%03d" % (ymdhms_strip, ms)

    @staticmethod
    def ymdhms2ts(s) -> int:
        ta = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(ta))

    @staticmethod
    def ymdhmsstrip2ts(s) -> int:
        ta = time.strptime(s, "%Y%m%d-%H%M%S")
        return int(time.mktime(ta))

    @staticmethod
    def ymd2ts(s) -> int:
        ta = time.strptime(s, "%Y-%m-%d")
        return int(time.mktime(ta))


_is_linux = platform.system().lower() == 'linux'


def is_x86() -> bool:
    if not _is_linux:
        return True
    try:
        x = os.popen("uname -a")
        for xx in x:
            if "x86_64" in xx:
                return True
    except:
        pass
    return False


__all__ = ['cal_str_md5', 'cal_file_md5', 'get_class_or_func', 'current_time', 'TimeNow', 'is_x86']
