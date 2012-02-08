"""
  Copyright (C) 2012 David Aguilar
  Copyright (C) 2007 Jan-Klaas Kollhof

  This file is part of jsonrpc.

  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

import unittest
import jsonrpc


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg

    def not_a_servicemethod(self):
        pass

    @jsonrpc.servicemethod
    def raiseError(self):
        raise Exception('foobar')


class Handler(jsonrpc.ServiceHandler):
    def __init__(self, service):
        self.service = service

    def translate_request(self, data):
        self._request_translated = True
        return super(Handler, self).translate_request(data)

    def findServiceEndpoint(self, name):
        self._foundServiceEndpoint=True
        return jsonrpc.ServiceHandler.findServiceEndpoint(self, name)

    def invokeServiceEndpoint(self, meth, params):
        self._invokedEndpoint=True
        return jsonrpc.ServiceHandler.invokeServiceEndpoint(self, meth, params)

    def translate_result(self, result, error, id_):
        self._resultTranslated=True
        return jsonrpc.ServiceHandler.translate_result(self, result, error,  id_)



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
        self.assertTrue(handler._foundServiceEndpoint)
        self.assertTrue(handler._invokedEndpoint)
        self.assertTrue(handler._resultTranslated)

    def test_translate_request(self):
        handler = Handler(self.service)
        json=jsonrpc.dumps({'method':'echo',
                            'params':['foobar'],
                            'id':''})
        req = handler.translate_request(json)
        self.assertEquals(req['method'], 'echo')
        self.assertEquals(req['params'],['foobar'])
        self.assertEquals(req['id'],'')

    def test_findServiceEndpoint(self):
        handler = Handler(self.service)
        self.assertRaises(jsonrpc.ServiceMethodNotFound,
                          handler.findServiceEndpoint, 'notfound')
        self.assertRaises(jsonrpc.ServiceMethodNotFound,
                          handler.findServiceEndpoint, 'not_a_servicemethod')
        echo = handler.findServiceEndpoint('echo')
        self.assertEquals(self.service.echo, echo)

    def test_invokeEndpoint(self):
        handler = Handler(self.service)
        meth = handler.findServiceEndpoint("echo")
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
        data=handler.translate_result(None, exc, 'id')
        self.assertEquals(jsonrpc.loads(data),
                          {'result': None,
                           'id':'id',
                           'error':{'name': 'Exception',
                                    'message': ''}})

    def test_translateUnencodableResults(self):
        handler=Handler(self.service)
        data=handler.translate_result(self, None, "spam")
        self.assertEquals(jsonrpc.loads(data), {"result":None,"id":"spam","error":{"name":"JSONEncodeException", "message":"Result Object Not Serializable"}})

    def test_handle_request_echo(self):
        handler=Handler(self.service)
        json=jsonrpc.dumps({'method':'echo', 'params':['foobar'], 'id':''})
        result = handler.handle_request(json)
        self.assertEquals(jsonrpc.loads(result), jsonrpc.loads('{"result":"foobar", "error":null, "id":""}'))

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
        json=jsonrpc.dumps({'method': 'raiseError',
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
