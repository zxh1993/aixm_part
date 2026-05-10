# @Time   : 2021-04-21
# @Author : zhangxinhao
# @Compile : True
import os
import sys
import hashlib
import platform

_system = platform.system().lower()
is_linux = _system == 'linux'
_is_supported_system = is_linux or _system == 'darwin'


def _require_supported_system():
    if not _is_supported_system:
        raise RuntimeError("目前只支持linux和macos")


def cal_str_md5(s) -> str:
    return hashlib.md5(s.encode()).hexdigest()


class PythonProcess:
    def __init__(self, run_file_path, src_path=None, ukey=''):
        _require_supported_system()
        self.run_file_path = run_file_path
        if src_path is None:
            file_path = os.path.realpath(run_file_path)
            index = file_path.find('/src/')
            if index == -1:
                print('src 目录不存在!')
                sys.exit(0)
            src_path = os.path.join(file_path[:index], 'src')
        self.src_path = src_path
        self.ukey = ukey

    def is_run(self, index=None) -> bool:
        uid = self.make_uid(index)
        lines = os.popen('ps -ef | grep %s | grep -v grep' % uid)
        for _ in lines:
            return True
        return False

    def stop(self, index=None):
        uid = self.make_uid(index)
        lines = os.popen('ps -ef | grep %s | grep -v grep' % uid)
        for line in lines:
            pid = int(line.split()[1])
            os.system('kill -9 %d' % pid)

    def start(self, index=None):
        self._run(True, index)

    def test(self, index=None):
        self._run(False, index)

    def keep_alive(self, index=None):
        if not self.is_run(index):
            self.start(index)

    def make_uid(self, index=None) -> str:
        uid = 'uid-' + cal_str_md5(self.run_file_path)[:12] + '-' + self.ukey + '-'
        if index is not None:
            uid = uid + str(index) + '-'
        return uid

    def _run(self, is_back, index=None):
        self.stop(index)
        if index is None:
            if is_back:
                command_format = "PYTHONPATH={src_path} nohup {python_bin} {filepath} {uid} >/dev/null 2>&1 &"
            else:
                command_format = "PYTHONPATH={src_path} {python_bin} {filepath} {uid}"
        else:
            if is_back:
                command_format = "PYTHONPATH={src_path} nohup {python_bin} {filepath} {index} {uid} >/dev/null 2>&1 &"
            else:
                command_format = "PYTHONPATH={src_path} {python_bin} {filepath} {index} {uid}"
        uid = self.make_uid(index)
        python_bin = sys.executable
        command = command_format.format(src_path=self.src_path,
                                        python_bin=python_bin,
                                        filepath=self.run_file_path,
                                        index=index,
                                        uid=uid)
        os.system(command)


class ExecProcess:
    def __init__(self, src_run_file_path, args_str=''):
        _require_supported_system()
        self.src_run_file_path = src_run_file_path
        self.args_str = args_str
        self.dst_run_file_path = src_run_file_path + '_' + self.make_uid()

        os.system('rm -rf %s' % self.dst_run_file_path)
        os.system('ln -s %s %s' % (self.src_run_file_path, self.dst_run_file_path))

    def is_run(self) -> bool:
        lines = os.popen('ps -ef | grep %s | grep -v grep' % os.path.basename(self.dst_run_file_path))
        for _ in lines:
            return True
        return False

    def stop(self):
        lines = os.popen('ps -ef | grep %s | grep -v grep' % os.path.basename(self.dst_run_file_path))
        for line in lines:
            pid = int(line.split()[1])
            os.system('kill -9 %d' % pid)

    def start(self):
        self._run(True)

    def test(self):
        self._run(False)

    def keep_alive(self):
        if not self.is_run():
            self.start()

    def make_uid(self):
        uid = cal_str_md5(self.src_run_file_path + self.args_str)[:16]
        return uid

    def _run(self, is_back):
        self.stop()
        if is_back:
            command_format = "nohup {filepath} {args_str} >/dev/null 2>&1 &"
        else:
            command_format = "{filepath} {args_str}"
        command = command_format.format(filepath=self.dst_run_file_path,
                                        args_str=self.args_str)
        command = command.replace('<exec_path>', self.dst_run_file_path)
        os.system(command)


__all__ = ['PythonProcess', 'ExecProcess']
