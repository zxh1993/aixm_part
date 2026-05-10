# @Time   : 2020-04-06
# @Author : zhangxinhao
# @Compile : True
from aixm._internal.path import *
from queue import Queue
import socket
import pickle
import struct
import datetime
import os
import threading
import traceback

_log_queue = Queue()
_app_dict = dict()
_format = '{log_time}|HN:{hostname}|AD:{ip}:{port}|LID:{log_id}|'
_format += 'PID:{process}|ATIME:{asctime}|LEV:{levelname}|({pathname}|{lineno}):{msg}\n'


def _log_thread():
    while True:
        try:
            now, data = _log_queue.get()
            appname = data['name']
            day = now[:10]
            log_file_info = _app_dict.get(appname)
            if log_file_info is None:
                os.makedirs(relative_logs_path(appname), exist_ok=True)
                fp = open(relative_logs_path(appname, day + '.log'), 'a')
                log_file_info = (fp, day)
                _app_dict[appname] = log_file_info
            else:
                fp, last_day = log_file_info
                if last_day != day:
                    fp.close()
                    os.makedirs(relative_logs_path(appname), exist_ok=True)
                    fp = open(relative_logs_path(appname, day + '.log'), 'a')
                    log_file_info = (fp, day)
                    _app_dict[appname] = log_file_info
            data['asctime'] = data['asctime'][11:]
            pathname = data['pathname'].replace('\\', '/')
            src_index = pathname.find('/src/')
            if src_index != -1:
                data['pathname'] = pathname[src_index + 5:]
            else:
                data['pathname'] = data['filename']
            fp = log_file_info[0]
            fp.write(_format.format(**data))
            fp.flush()
        except:
            traceback.print_exc()


def start_logging_server(host='0.0.0.0', port=6666):
    lt = threading.Thread(target=_log_thread, args=())
    lt.start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            ip, port = addr
            len_ = struct.unpack('>L', data[:4])[0]
            data = pickle.loads(data[4:4 + len_])
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            data['ip'] = ip
            data['port'] = port
            data['log_time'] = now
            _log_queue.put_nowait((now, data))
        except:
            traceback.print_exc()


__all__ = ['start_logging_server']
