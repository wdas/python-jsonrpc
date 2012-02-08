import unittest
import jsonrpc


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg

    def not_a_servicemethod(self):
        pass

    @jsonrpc.servicemethod
    def raise_error(self):
        raise Exception('foobar')


class Handler(jsonrpc.ServiceHandler):
    def __init__(self, service):
        self.service = service

    def translate_request(self, data):
        self._request_translated = True
        return super(Handler, self).translate_request(data)

    def find_service_method(self, name):
        self._found_service_method =True
        return jsonrpc.ServiceHandler.find_service_method(self, name)

    def call_service_method(self, meth, params):
        self._service_method_called = True
        return super(Handler, self).call_service_method(meth, params)

    def translate_result(self, result, error, id_):
        self._result_translated = True
        return jsonrpc.ServiceHandler.translate_result(self, result,
                                                       error, id_)


class  TestServiceHandler(unittest.TestCase):

    def setUp(self):
        self.service = Service()

    def tearDown(self):
        pass

    def test_RequestProcessing(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method':'echo',
                              'params':['foobar'], 'id':''})

        handler.handle_request(json)
        self.assertTrue(handler._request_translated)
        self.assertTrue(handler._found_service_method)
        self.assertTrue(handler._invokedEndpoint)
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

    def test_invokeEndpoint(self):
        handler = Handler(self.service)
        meth = handler.find_service_method('echo')
        rslt = handler.invokeServiceEndpoint(meth, ['spam'])
        self.assertEquals(rslt, 'spam')

    def test_translate_results(self):
        handler = Handler(self.service)
        data = handler.translate_result('foobar', None,  'spam')
        self.assertEquals(jsonrpc.loads(data),
                          {'result': 'foobar', 'id': 'spam', 'error': None})

    def test_translateError(self):
        handler=Handler(self.service)
        exc = Exception()
        data = handler.translate_result(None, exc, 'id')
        self.assertEquals(jsonrpc.loads(data),
                          {'result': None,
                           'id':'id',
                           'error':{'name': 'Exception',
                                    'message': ''}})

    def test_translateUnencodableResults(self):
        handler = Handler(self.service)
        data = handler.translate_result(self, None, 'spam')
        message = 'Result Object Not Serializable'
        self.assertEquals(jsonrpc.loads(data),
                          {'result': None,
                           'id': 'spam',
                           'error': {'name': 'JSONEncodeException',
                                     'message': message}})

    def test_handle_request_echo(self):
        handler = Handler(self.service)
        json = jsonrpc.dumps({'method':'echo',
                              'params':['foobar'],
                              'id':''})
        expected = '{"result":"foobar", "error":null, "id":""}'
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          jsonrpc.loads(expected))

    def test_handle_request_MethodNotFound(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({"method":"not_found", 'params':['foobar'], 'id':''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result), {"result":None, "error":{"name":"ServiceMethodNotFound", "message":""}, "id":""})

    def test_handle_request_MethodNotAllowed(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({'method': 'not_a_servicemethod',
                            'params':['foobar'],
                            'id':''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'result':None,
                           'error': {'name': 'ServiceMethodNotFound',
                                     'message': ''},
                           'id': ''})

    def test_handle_request_MethodRaiseError(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({'method': 'raise_error',
                            'params': [],
                            'id': ''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'result': None,
                           'error': {'name':'Exception',
                                     'message':'foobar'},
                           'id':''})

    def test_handle_request_BadRequestData(self):
        handler=Handler(self.service)
        json = 'This is not a JSON-RPC request'
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'result': None,
                           'error': {'name': 'ServiceRequestNotTranslatable',
                                     'message':json},
                           'id':''})

    def test_handle_request_BadRequestObject(self):
        handler=Handler(self.service)
        json = '{}'
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result),
                          {'result': None,
                           'error': {'name': 'BadServiceRequest',
                                     'message':json},
                           'id':''})
