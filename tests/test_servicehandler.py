import unittest
import jsonrpc
from jsonrpc import servicemethod


class Service(object):
    @servicemethod
    def echo(self, arg):
        return arg

    @servicemethod
    def echo_kwargs(self, **kwargs):
        return kwargs

    def not_a_servicemethod(self):
        pass

    @servicemethod
    def raise_error(self):
        raise Exception('foobar')


class Handler(jsonrpc.ServiceHandler):
    def __init__(self, service):
        super(Handler, self).__init__(service)

    def translate_request(self, data):
        self._request_translated = True
        return super(Handler, self).translate_request(data)

    def find_service_method(self, name):
        self._found_service_method =True
        return super(Handler, self).find_service_method(name)

    def call_service_method(self, meth, params):
        self._service_method_called = True
        return super(Handler, self).call_service_method(meth, params)

    def translate_result(self, result, error, id_, trace):
        self._result_translated = True
        return super(Handler, self).translate_result(result, error, id_, trace)


class  TestServiceHandler(unittest.TestCase):

    def setUp(self):
        self.service = Service()

    def tearDown(self):
        pass

    def test_request_processing(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method':'echo',
                              'params':['foobar'], 'id':''})

        handler.handle_request(json)
        self.assertTrue(handler._request_translated)
        self.assertTrue(handler._found_service_method)
        self.assertTrue(handler._service_method_called)
        self.assertTrue(handler._result_translated)

    def test_request_processing_kwargs(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method': 'echo_kwargs',
                              'params': {'foobar': True},
                              'id':''})
        handler.handle_request(json)
        self.assertTrue(handler._request_translated)
        self.assertTrue(handler._found_service_method)
        self.assertTrue(handler._service_method_called)
        self.assertTrue(handler._result_translated)

    def test_translate_request(self):
        handler = Handler(self.service)
        json=jsonrpc.dumps({'method':'echo',
                            'params':['foobar'],
                            'id':''})
        req = handler.translate_request(json)
        self.assertEquals(req['method'], 'echo')
        self.assertEquals(req['params'],['foobar'])
        self.assertEquals(req['id'],'')

    def test_find_service_method(self):
        handler = Handler(self.service)
        self.assertRaises(jsonrpc.ServiceMethodNotFound,
                          handler.find_service_method, 'notfound')
        self.assertRaises(jsonrpc.ServiceMethodNotFound,
                          handler.find_service_method, 'not_a_servicemethod')
        echo = handler.find_service_method('echo')
        self.assertEquals(self.service.echo, echo)

    def test_call_service_method(self):
        handler = Handler(self.service)
        meth = handler.find_service_method('echo')
        rslt = handler.call_service_method(meth, ['spam'])
        self.assertEquals(rslt, 'spam')

    def test_translate_results(self):
        handler = Handler(self.service)
        data = handler.translate_result('id', 'foobar', None,  None)
        self.assertEquals(jsonrpc.loads(data),
                {'jsonrpc': '2.0', 'result': 'foobar', 'id': 'id'})

    def test_translate_error(self):
        handler=Handler(self.service)
        exc = Exception()
        data = handler.translate_result('id', None, exc, None)
        self.assertEquals(jsonrpc.loads(data),
                          {'id':'id',
                           'error':{'code': -32603,
                                    'message': ''}})

    def test_translate_unencodable_results(self):
        handler = Handler(self.service)
        data = handler.translate_result('id', self, None, None)
        error = {
                'message': 'Internal JSON-RPC error',
                'code': -32603,
        }
        self.assertEquals(jsonrpc.loads(data),
                          {'id': 'id',
                           'error': error})

    def test_handle_request_echo(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method':'echo',
                              'params':['foobar'],
                              'id':''})
        expected = '{"result":"foobar", "id":"", "jsonrpc":"2.0"}'
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          jsonrpc.loads(expected))

    def test_handle_request_MethodNotFound(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({'method': 'not_found',
                            'params': ['foobar'],
                            'id':''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                {'error': { 'message':'Method not found: not_found',
                            'code': -32601},
                 'id':''})

    def test_handle_request_MethodNotAllowed(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({'method': 'not_a_servicemethod',
                            'params':['foobar'],
                            'id':''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'error': {
                              'message':
                                    'Method not found: not_a_servicemethod',
                              'code': -32601},
                           'id': ''})

    def test_handle_request_MethodRaiseError(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({'method': 'raise_error',
                            'params': [],
                            'id': ''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'error': {'code': -32603,
                                     'message': 'foobar'},
                           'id':''})

    def test_handle_request_BadRequestData(self):
        handler=Handler(self.service)
        json = 'This is not a JSON-RPC request'
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'error': {'message': 'Parse error',
                                     'code': -32700},
                           'id': None})

    def test_handle_request_BadRequestObject(self):
        handler=Handler(self.service)
        json = '{}'
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'error': {'message': 'Invalid Request',
                                     'code': -32600},
                           'id': None})
