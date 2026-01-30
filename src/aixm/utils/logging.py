# @Time   : 2020-04-05
# @Author : zhangxinhao
# @Compile : True
from .project_path import relative_logs_path, DIR_SPLIT
import threading
import logging
import logging.handlers
import sys
import os
import pickle
import struct
import socket
import datetime

_log_mutex = threading.Lock()
_logger_dict = dict()


class LocalFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, rotating_conf=None):
        if rotating_conf is None:
            rotating_conf = {'when': 'W0', 'interval': 1, 'backupCount': 53}
        os.makedirs(relative_logs_path(), exist_ok=True)
        logfile = relative_logs_path(filename + ".log")
        super().__init__(logfile, when=rotating_conf['when'],
                         interval=rotating_conf['interval'],
                         backupCount=rotating_conf['backupCount'])
        formatter = logging.Formatter("[%(asctime)s|%(levelname)s][%(filename)s|%(lineno)d]:%(message)s")
        self.setFormatter(formatter)


class ConsoleHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        formatter = logging.Formatter("[%(asctime)s|%(levelname)s][%(filename)s|%(lineno)d]:%(message)s")
        self.setFormatter(formatter)


class CollectHandler(logging.handlers.DatagramHandler):
    def __init__(self, host, port, log_id):
        super().__init__(host, port)
        self.hostname = socket.gethostname()
        self.log_id = log_id

    def makePickle(self, record):
        ei = record.exc_info
        if ei:
            dummy = self.format(record)
        d = dict(record.__dict__)
        msg = record.getMessage()
        if len(msg) > 3072:
            msg = msg[:3072]
        d['msg'] = msg
        d['args'] = None
        d['exc_info'] = None
        d['log_id'] = self.log_id
        if d.get('asctime') is None:
            d['asctime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        d['hostname'] = self.hostname
        d.pop('message', None)
        s = pickle.dumps(d, 1)
        slen = struct.pack(">L", len(s))
        return slen + s


def init_logger(appname=None, filename=None, log_id=None, exist_ok=False,
                open_console=True, open_localfile=True, open_collect=False, level='DEBUG',
                rotating_conf=None,
                collect_address=('localhost', 6666), to_default=True):  # (
    if rotating_conf is None:
        rotating_conf = {'when': 'W0', 'interval': 1, 'backupCount': 53}  # )
    with _log_mutex:  # 日志只初始化一次
        if _logger_dict.get(appname) is not None:
            if exist_ok:
                return
            raise Exception(appname + '日志初始化两次!')
        if appname is None:
            run_path = os.path.realpath(sys.argv[0])
            appname = run_path[run_path.rfind(DIR_SPLIT) + 1:-3]  # 初始化为文件名
        if filename is None:
            filename = appname
        logger = logging.getLogger(appname)
        logger.setLevel(level)
        if open_console:
            logger.addHandler(ConsoleHandler())

        if open_localfile:
            logger.addHandler(LocalFileHandler(filename, rotating_conf))

        if open_collect:
            logger.addHandler(CollectHandler(collect_address[0], collect_address[1], log_id))

        logger.propagate = 0  # 修复打印两次错误
        _logger_dict[appname] = logger
        if to_default:
            set_default_logger(logger)
        return logger


_default_logger = logging.getLogger()
_default_logger.setLevel('INFO')
_default_logger.addHandler(ConsoleHandler())


def log(appname=None) -> logging.Logger:
    if appname is None:
        return _default_logger
    logger = _logger_dict.get(appname)
    assert logger is not None, appname + ' 日志未初始化!'
    return logger


def set_default_logger(logger):
    global _default_logger
    _default_logger = logger


'''
#copy-begin
import logging
#copy-end
'''
__all__ = ['init_logger', 'log']
