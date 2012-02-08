import urllib
from jsonrpc.json import dumps, loads


class JSONRPCException(Exception):
    def __init__(self, error):
        Exception.__init__(self)
        self.error = error


class ServiceProxy(object):
    def __init__(self, url, name=None):
        self._url = url
        self._name = name

    def __getattr__(self, name):
        if self._name is not None:
            name = '%s.%s' % (self._name, name)
        return ServiceProxy(self._url, name)

    def __call__(self, *args):
         postdata = dumps({'method': self._name,
                           'params': args,
                           'id': 'jsonrpc'})
         respdata = urllib.urlopen(self._url, postdata).read()
         resp = loads(respdata)
         if resp.get('error', None) is not None:
             raise JSONRPCException(resp['error'])
         else:
             return resp.get('result', None)
