import sys
import unittest

import jsonrpc
from jsonrpc import servicemethod
from jsonrpc import servicehandler


class Service(object):
    @servicemethod
    def echo(self, arg):
        return arg

    @servicemethod
    def echo_kwargs(self, **kwargs):
        return kwargs

    @servicemethod
    def raise_error(self):
        raise Exception('foobar')

    def decorator_is_optional(self):
        return ['yes', True]


class Handler(jsonrpc.ServiceHandler):
    def __init__(self, service):
        super(Handler, self).__init__(service)

    def translate_request(self, data):
        self._request_translated = True
        return super(Handler, self).translate_request(data)

    def find_service_method(self, name):
        self._found_service_method = True
        return super(Handler, self).find_service_method(name)

    def call_service_method(self, meth, params):
        self._service_method_called = True
        return super(Handler, self).call_service_method(meth, params)

    def translate_result(self, result, error, id_, trace):
        self._result_translated = True
        return super(Handler, self).translate_result(result, error, id_, trace)


class TestServiceHandler(unittest.TestCase):
    def setUp(self):
        self.service = Service()

    def test_get_service_method(self):
        obj = dict(name=42)
        actual = servicehandler.get_service_method(obj, 'name')
        expect = 42
        self.assertEqual(expect, actual)

    def test_request_processing(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method': 'echo', 'params': ['foobar'], 'id': ''})

        handler.handle_request(json)
        self.assertTrue(handler._request_translated)
        self.assertTrue(handler._found_service_method)
        self.assertTrue(handler._service_method_called)
        self.assertTrue(handler._result_translated)

    def test_request_processing_kwargs(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps(
            {'method': 'echo_kwargs', 'params': {'foobar': True}, 'id': ''}
        )
        handler.handle_request(json)
        self.assertTrue(handler._request_translated)
        self.assertTrue(handler._found_service_method)
        self.assertTrue(handler._service_method_called)
        self.assertTrue(handler._result_translated)

    def test_translate_request(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method': 'echo', 'params': ['foobar'], 'id': ''})
        req = handler.translate_request(json)
        self.assertEqual(req['method'], 'echo')
        self.assertEqual(req['params'], ['foobar'])
        self.assertEqual(req['id'], '')

    def test_find_service_method(self):
        handler = Handler(self.service)
        self.assertRaises(
            jsonrpc.ServiceMethodNotFound, handler.find_service_method, 'notfound'
        )
        echo = handler.find_service_method('echo')
        self.assertEqual(self.service.echo, echo)

        method = handler.find_service_method('decorator_is_optional')
        self.assertEqual(self.service.decorator_is_optional, method)

    def test_call_service_method(self):
        handler = Handler(self.service)
        meth = handler.find_service_method('echo')
        rslt = handler.call_service_method(meth, ['spam'])
        self.assertEqual(rslt, 'spam')

    def test_translate_results(self):
        handler = Handler(self.service)
        data = handler.translate_result('id', 'foobar', None, None)
        self.assertEqual(
            jsonrpc.loads(data), {'jsonrpc': '2.0', 'result': 'foobar', 'id': 'id'}
        )

    def test_translate_error(self):
        handler = Handler(self.service)
        exc = Exception()
        data = handler.translate_result('id', None, exc, None)
        self.assertEqual(
            jsonrpc.loads(data), {'id': 'id', 'error': {'code': -32603, 'message': ''}}
        )

    def test_translate_unencodable_results(self):
        handler = Handler(self.service)
        data = handler.translate_result('id', self, None, None)
        error = {
            'message': 'Internal JSON-RPC error',
            'code': -32603,
        }
        self.assertEqual(jsonrpc.loads(data), {'id': 'id', 'error': error})

    def test_handle_request_echo(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method': 'echo', 'params': ['foobar'], 'id': ''})
        expected = '{"result":"foobar", "id":"", "jsonrpc":"2.0"}'
        result = handler.handle_request(json)
        self.assertEqual(jsonrpc.loads(result), jsonrpc.loads(expected))

    def test_handle_request_MethodNotFound(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method': 'not_found', 'params': ['foobar'], 'id': ''})
        result = handler.handle_request(json)
        self.assertEqual(
            jsonrpc.loads(result),
            {
                'error': {'message': 'Method not found: not_found', 'code': -32601},
                'id': '',
            },
        )

    def test_handle_request_MethodRaiseError(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method': 'raise_error', 'params': [], 'id': ''})
        result = handler.handle_request(json)
        self.assertEqual(
            jsonrpc.loads(result),
            {'error': {'code': -32603, 'message': 'foobar'}, 'id': ''},
        )

    def test_handle_request_BadRequestData(self):
        handler = Handler(self.service)
        json = 'This is not a JSON-RPC request'
        result = handler.handle_request(json)
        self.assertEqual(
            jsonrpc.loads(result),
            {'error': {'message': 'Parse error', 'code': -32700}, 'id': None},
        )

    def test_handle_request_BadRequestObject(self):
        handler = Handler(self.service)
        json = '{}'
        result = handler.handle_request(json)
        self.assertEqual(
            jsonrpc.loads(result),
            {'error': {'message': 'Invalid Request', 'code': -32600}, 'id': None},
        )


class TestUtilityMethods(unittest.TestCase):
    def test_get_callables(self):
        callables = servicehandler.get_callables(sys.modules[__name__])
        module_found = False
        for k, v in callables:
            if k == self.__class__.__name__:
                module_found = True
                break
        self.assertTrue(module_found)


if __name__ == '__main__':
    unittest.main()
