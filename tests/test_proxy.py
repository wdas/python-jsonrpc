from __future__ import absolute_import, division, unicode_literals
import unittest

from mock import patch

import jsonrpc
from jsonrpc.compat import httplib  # noqa


class MockHTTPConnection(object):
    current = None

    def __init__(self, *args, **kwargs):
        MockHTTPConnection.current = self
        self.postdata = b''
        self.respdata = b''

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


def setup_mock_httplib(mock_httplib):
    mock_httplib.HTTPConnection = http_factory
    mock_httplib.HTTPSConnection = http_factory


@patch('jsonrpc.proxy.httplib')
class TestProxy(unittest.TestCase):
    def test_provides_proxy_method(self, mock_httplib):
        setup_mock_httplib(mock_httplib)
        s = jsonrpc.ServiceProxy("http://localhost/")
        assert callable(s.echo)

    def test_method_call(self, mock_httplib):
        setup_mock_httplib(mock_httplib)
        s = jsonrpc.ServiceProxy("http://localhost/")

        http = MockHTTPConnection.current
        http.respdata = b'{"result":"foobar","error":null,"id": 1}'

        echo = s.echo('foobar')
        expect = jsonrpc.dumps(
            {'id': 1, 'jsonrpc': '2.0', 'method': 'echo', 'params': ['foobar']}
        )
        assert expect == MockHTTPConnection.current.postdata
        assert echo == 'foobar'

        http.respdata = b'{"result":null,"error":"MethodNotFound","id":""}'
        try:
            s.echo('foobar')
        except jsonrpc.JSONRPCException as e:
            assert e.error == 'MethodNotFound'

    def test_method_call_with_kwargs(self, mock_httplib):
        setup_mock_httplib(mock_httplib)
        s = jsonrpc.ServiceProxy("http://localhost/")

        http = MockHTTPConnection.current
        http.respdata = b'{"result": {"foobar": true},"error": null, "id": 1}'

        echo = s.echo_kwargs(foobar=True)
        expect = jsonrpc.dumps(
            {
                'id': 1,
                'jsonrpc': '2.0',
                'method': 'echo_kwargs',
                'params': {'foobar': True},
            }
        )
        assert expect == MockHTTPConnection.current.postdata
        assert echo == {'foobar': True}
