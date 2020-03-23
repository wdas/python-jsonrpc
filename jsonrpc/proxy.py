import base64
import decimal

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

from jsonrpc.json import dumps, loads
from jsonrpc.compat import httplib

USER_AGENT = 'python-jsonrpc/2.0'


class JSONRPCException(Exception):
    def __init__(self, error):
        super(JSONRPCException, self).__init__()
        self.error = error


class ServiceProxy(object):
    def __init__(
        self, service_url, name=None, encoding='utf8', timeout=None, use_decimal=False
    ):
        self._service_url = service_url
        self._name = name
        self._idcnt = 0
        self._jsonrpc = '2.0'
        self._use_decimal = use_decimal
        self._encoding = encoding

        self._url = urlparse.urlparse(service_url)
        if self._url.port is None:
            port = 80
        else:
            port = self._url.port

        if self._url.scheme == 'https':
            self._conn = httplib.HTTPSConnection(
                self._url.hostname, port, timeout=timeout
            )
        else:
            self._conn = httplib.HTTPConnection(
                self._url.hostname, port, timeout=timeout
            )

        self._headers = {
            'Host': self._url.hostname,
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json',
        }

        username = self._url.username
        password = self._url.password
        if username and password:
            authpair = (username + ':' + password).encode(self._encoding)
            authhdr = 'Basic ' + base64.b64encode(authpair)
            self._headers['Authorization'] = authhdr

    def __getattr__(self, name):
        if self._name is not None:
            name = '%s.%s' % (self._name, name)
        return ServiceProxy(self._service_url, name)

    def __call__(self, *args, **kwargs):
        """Issue a remote procedure call using JSON-RPC 2.0"""
        self._idcnt += 1

        if args and kwargs:
            raise JSONRPCException(
                {
                    'code': -32600,
                    'message': 'Cannot use both positional '
                    'and keyword arguments '
                    '(according to JSON-RPC spec.)',
                }
            )

        postdata = dumps(
            {
                'id': self._idcnt,
                'jsonrpc': self._jsonrpc,
                'method': self._name,
                'params': args or kwargs,
            }
        )
        self._conn.request('POST', self._url.path, postdata, self._headers)

        httpresp = self._conn.getresponse()
        if httpresp is None:
            raise JSONRPCException(
                {'code': -342, 'message': 'missing HTTP response from the server'}
            )

        resp = httpresp.read().decode(self._encoding)
        if self._use_decimal:
            resp = loads(resp, parse_float=decimal.Decimal)
        else:
            resp = loads(resp)

        error = resp.get('error', None)
        if error is not None:
            raise JSONRPCException(error)

        try:
            return resp['result']
        except KeyError:
            raise JSONRPCException(
                {'code': -32600, 'message': 'missing result in JSON response'}
            )
