from traceback import format_exc
from jsonrpc import loads, dumps, JSONEncodeException


def servicemethod(fn):
    fn.jsonrpc_servicemethod = True
    return fn


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
        tracebacks = self.tracebacks

        try:
            req = self.translate_request(json)
        except ParseError, e:
            if tracebacks:
                trace = format_exc()
            return self.translate_result(id_, result, e, trace)
        try:
            id_ = req['id']
            method = req['method']
            args = req['params']
        except Exception, e:
            if tracebacks:
                trace = format_exc()
            e = InvalidRequest(json)
            return self.translate_result(id_, result, e, trace)

        try:
            meth = self.find_service_method(method)
        except Exception, e:
            if tracebacks:
                trace = format_exc()
            return self.translate_result(id_, result, e, trace)

        try:
            result = self.call_service_method(meth, args)
        except Exception, e:
            if tracebacks:
                trace = format_exc()
            return self.translate_result(id_, result, e, trace)

        return self.translate_result(id_, result, None, None)

    def translate_request(self, data):
        try:
            return loads(data)
        except:
            raise ParseError(data)

    def find_service_method(self, name):
        try:
            meth = getattr(self.service, name)
            if getattr(meth, 'jsonrpc_servicemethod'):
                return meth
            else:
                raise ServiceMethodNotFound(name)
        except AttributeError:
            raise ServiceMethodNotFound(name)

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
                error['message'] = unicode(err)

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
