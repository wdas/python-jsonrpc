import unittest
import jsonrpc

import urllib

from StringIO import StringIO

class  TestProxy(unittest.TestCase):

    def urlopen(self, url, data):
        self.postdata = data
        return StringIO(self.respdata) 
    
    def setUp(self):
        self.postdata=""
        self.urllib_openurl = urllib.urlopen
        urllib.urlopen = self.urlopen
        
    def tearDown(self):
        urllib.urlopen = self.urllib_openurl

    def test_ProvidesProxyMethod(self):
        s = jsonrpc.ServiceProxy("http://localhost/")
        self.assert_(callable(s.echo))

    def test_MethodCallCallsService(self):
        
        s = jsonrpc.ServiceProxy("http://localhost/")

        self.respdata='{"result":"foobar","error":null,"id":""}'
        echo = s.echo("foobar")
        self.assertEquals(self.postdata, jsonrpc.dumps({"method":"echo", 'params':['foobar'], 'id':'jsonrpc'}))
        self.assertEquals(echo, 'foobar')

        self.respdata='{"result":null,"error":"MethodNotFound","id":""}'
        try:
            s.echo("foobar")
        except jsonrpc.JSONRPCException,e:
            self.assertEquals(e.error, "MethodNotFound")
            