import unittest
import jsonrpc

try:
    import http.client as httplib
except ImportError:
    import httplib


class MockHTTPConnection(object):
    current = None

    def __init__(self, *args, **kwargs):
        MockHTTPConnection.current = self
        self.postdata = ''
        self.respdata = ''

    def getresponse(self):
        return self

    def request(self, method, url, postdata, headers):
        self.method = method
        self.url = url
        self.postdata = postdata
        self.headers = headers

    def read(self):
        return self.respdata


def http_factory(*args, **kwargs):
    if MockHTTPConnection.current:
        return MockHTTPConnection.current
    return MockHTTPConnection(*args, **kwargs)


class TestProxy(unittest.TestCase):

    def setUp(self):
        self.real_http = httplib.HTTPConnection
        self.real_https = httplib.HTTPSConnection
        httplib.HTTPConnection = http_factory
        httplib.HTTPSConnection = http_factory

    def tearDown(self):
        if MockHTTPConnection.current:
            MockHTTPConnection.current = None
        httplib.HTTPConnection = self.real_http
        httplib.HTTPSConnection = self.real_https

    def test_provides_proxy_method(self):
        s = jsonrpc.ServiceProxy("http://localhost/")
        self.assert_(callable(s.echo))

    def test_method_call(self):
        s = jsonrpc.ServiceProxy("http://localhost/")

        http = MockHTTPConnection.current
        http.respdata = '{"result":"foobar","error":null,"id": 1}'

        echo = s.echo('foobar')
        self.assertEquals(MockHTTPConnection.current.postdata,
                          jsonrpc.dumps({
                              'id': 1,
                              'jsonrpc': '2.0',
                              'method':'echo',
                              'params': ['foobar'],
                           }))
        self.assertEquals(echo, 'foobar')

        http.respdata='{"result":null,"error":"MethodNotFound","id":""}'
        try:
            s.echo('foobar')
        except jsonrpc.JSONRPCException as e:
            self.assertEquals(e.error, 'MethodNotFound')

    def test_method_call_with_kwargs(self):
        s = jsonrpc.ServiceProxy("http://localhost/")

        http = MockHTTPConnection.current
        http.respdata = '{"result": {"foobar": true},"error":null,"id": 1}'

        echo = s.echo_kwargs(foobar=True)
        self.assertEquals(MockHTTPConnection.current.postdata,
                          jsonrpc.dumps({
                              'id': 1,
                              'jsonrpc': '2.0',
                              'method':'echo_kwargs',
                              'params': {'foobar': True},
                           }))
        self.assertEquals(echo, {'foobar': True})
