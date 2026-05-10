# @Time   : 2020-04-08
# @Author : zhangxinhao
# @Compile : True
import hashlib
import os
import datetime
import time
import math


def cal_str_md5(s) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def cal_file_md5(filepath) -> str:
    md5file = open(filepath, 'rb')
    md5 = hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    return md5


def remove_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)


def encrypt(src_file, dest_file, secret_key, block_size=16):
    f_out = open(dest_file, 'wb')
    index = 0
    secret_key = secret_key.encode()
    secret_key_len = len(secret_key)
    with open(src_file, 'rb') as f:
        while True:
            s = f.read(block_size)
            f_out.write(s)
            if len(s) < block_size:
                break
            s = f.read(1)
            if len(s) < 1:
                break
            f_out.write(bytes([(int(s[0]) + int(secret_key[index])) % 256]))
            index = (index + 1) % secret_key_len
    f_out.close()


def decrypt(src_file, dest_file, secret_key, block_size=16):
    f_out = open(dest_file, 'wb')
    index = 0
    secret_key = secret_key.encode()
    secret_key_len = len(secret_key)
    with open(src_file, 'rb') as f:
        while True:
            s = f.read(block_size)
            f_out.write(s)
            if len(s) < block_size:
                break
            s = f.read(1)
            if len(s) < 1:
                break
            f_out.write(bytes([(int(s[0]) - int(secret_key[index]) + 256) % 256]))
            index = (index + 1) % secret_key_len
    f_out.close()


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


__all__ = ['cal_str_md5', 'cal_file_md5', 'remove_file', 'encrypt', 'decrypt', 'current_time', 'TimeNow']
