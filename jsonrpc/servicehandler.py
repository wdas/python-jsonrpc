from traceback import format_exc
from jsonrpc import loads, dumps, JSONEncodeException

try:
    ustr = unicode
except NameError:
    # python3
    ustr = str


def servicemethod(fn):
    """Decorate a method to declare it as a service

    Do not use this decorator.  It is provided for compatibility only,
    and does not do anything.

    Originally, this decorator did this,

    > fn.jsonrpc_servicemethod = True

    and ServiceHandler would enforce the presence of the `jsonrpc_servicemethod`
    attribute at runtime.

    ServiceHandler was changed to not care whether or not this decorator was
    used.  This is simpler, faster, and makes the API easier to use.

    Although this decorator does not need to be used anymore, it will never be
    removed from the API in order to avoid needing to change working code.

    One benefit it does provide, besides backwards-compat, is that you can
    grep your code for @servicemethod and find all of them.

    """
    return fn


def servicemodule(module):
    """Return a dict(name=func) of functions from a module

    The resulting dictionary can be passed to :class:`ServiceHandler`
    when defining a service.

    """
    return dict(get_callables(module.__dict__.items()))


def get_callables(items):
    return [(k, v) for (k, v) in items
                if not k.startswith('_') and callable(v)]


def get_service_method(service, name):
    """Return a service method

    Raises ServiceMethodNotFound if the service could not be found.

    """
    try:
        if hasattr(service, '__getitem__'):
            meth = service[name]
        else:
            meth = getattr(service, name)
        return meth
    except (KeyError, AttributeError):
        pass
    raise ServiceMethodNotFound(name)


class ServiceException(Exception):
    jsonrpc_error_code = -32000
    jsonrpc_error_msg = 'Server error'


class ParseError(ServiceException):
    jsonrpc_error_code = -32700
    jsonrpc_error_msg = 'Parse error'


class InvalidRequest(ServiceException):
    jsonrpc_error_code = -32600
    jsonrpc_error_msg = 'Invalid Request'


class ServiceMethodNotFound(ServiceException):
    jsonrpc_error_code = -32601
    def __init__(self, method_name):
        self.method_name = method_name
        self.jsonrpc_error_msg = 'Method not found: %s' % method_name


class ServiceHandler(object):

    def __init__(self, service, tracebacks=False):
        self.service = service
        self.tracebacks = tracebacks

    def handle_request(self, json):
        result = None
        id_ = None
        trace = None
        err = None
        phase = 0
        tracebacks = self.tracebacks

        try:
            req = self.translate_request(json)
            phase = 1
            id_ = req['id']
            method = req['method']
            args = req['params']

            phase = 2
            meth = self.find_service_method(method)
            result = self.call_service_method(meth, args)
        except (ParseError, Exception) as err:
            if tracebacks:
                trace = format_exc()
            if phase == 1:
                err = InvalidRequest(json)

        return self.translate_result(id_, result, err, trace)

    def find_service_method(self, name):
        return get_service_method(self.service, name)

    def translate_request(self, data):
        try:
            return loads(data)
        except:
            raise ParseError(data)

    def call_service_method(self, meth, args):
        if type(args) is dict:
            return meth(**args)
        else:
            return meth(*args)

    def translate_result(self, id_, rslt, err, trace):
        if err is not None:
            error = {}

            if hasattr(err, 'jsonrpc_error_msg'):
                error['message'] = err.jsonrpc_error_msg
            else:
                error['message'] = ustr(err)

            if hasattr(err, 'jsonrpc_error_code'):
                error['code'] = err.jsonrpc_error_code
            else:
                error['code'] = -32603

            if trace:
                error['data'] = trace

            return dumps({'id': id_, 'error': error})

        try:
            return dumps({'jsonrpc': '2.0',
                          'id': id_,
                          'result': rslt})
        except JSONEncodeException:
            error = {
                    'message': 'Internal JSON-RPC error',
                    'code': -32603,
            }
            if trace:
                error['data'] = trace
            return dumps({'id': id_, 'error': error})
