# @Time   : 2019-06-21
# @Author : zhangxinhao
# @Compile : True
import contextvars
from functools import partial

# 创建 ContextVar
_ctx_var = contextvars.ContextVar('context')


def lookup_ctx_object(name=None):
    try:
        top = _ctx_var.get()
    except LookupError:
        raise RuntimeError('ctx_err_msg: ' + (name or 'context'))

    if name is None:
        return top
    return top[name]


# 创建代理对象，使用相同的接口
class ContextProxy:
    def __init__(self, func):
        self._func = func

    def __getattr__(self, name):
        return getattr(self._func(), name)

    def __getitem__(self, key):
        return self._func()[key]

    def __setitem__(self, key, value):
        self._func()[key] = value

    def __delitem__(self, key):
        del self._func()[key]

    def __contains__(self, key):
        return key in self._func()

    def __iter__(self):
        return iter(self._func())

    def __len__(self):
        return len(self._func())

    def __bool__(self):
        try:
            return bool(self._func())
        except RuntimeError:
            return False

    def __repr__(self):
        try:
            return repr(self._func())
        except RuntimeError:
            return '<Context not available>'


context = ContextProxy(lookup_ctx_object)
request = ContextProxy(partial(lookup_ctx_object, 'request'))
response = ContextProxy(partial(lookup_ctx_object, 'response'))
catch = ContextProxy(partial(lookup_ctx_object, 'catch'))


def new_context():
    ctx = dict()
    ctx['catch'] = dict()
    _ctx_var.set(ctx)
    return ctx


'''
#copy-begin
request = None # type: Request
response = None # type: Response
catch = None # type: dict
#copy-end
'''

__all__ = ['request', 'response', 'catch']