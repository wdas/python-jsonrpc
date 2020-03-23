from __future__ import absolute_import, division, unicode_literals
import unittest
import sys

import jsonrpc
from jsonrpc.compat import StringIO
from jsonrpc.compat import uchr


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg


class ApacheRequestMockup(object):
    def __init__(self, filename, fin, fout):
        self.fin = fin
        self.fout = fout
        self.filename = filename

    def write(self, data):
        self.fout.write(data)

    def flush(self):
        pass

    def read(self):
        return self.fin.read()


class ModPyMockup(object):
    def __init__(self):
        self.apache = ApacheModuleMockup()


class ApacheModuleMockup(object):
    def __getattr__(self, name):
        return name

    def import_module(self, moduleName, log=1):
        return Service()


class TestModPyWrapper(unittest.TestCase):
    def setUp(self):
        sys.modules['mod_python'] = ModPyMockup()

    def tearDown(self):
        del sys.modules['mod_python']

    def test_mod_python_handler(self):
        json = '{"method":"echo","params":["foobar"], "id":""}'
        fin = StringIO(json)
        fout = StringIO()
        req = ApacheRequestMockup(__file__, fin, fout)

        jsonrpc.handler(req)
        data = fout.getvalue()
        expect = {
            'result': 'foobar',
            'jsonrpc': '2.0',
            'id': '',
        }
        actual = jsonrpc.loads(data)
        self.assertEqual(expect, actual)

    def test_service_implementation_not_found(self):
        json = '{"method":"echo","params":["foobar"], "id":""}'
        fin = StringIO(json)
        fout = StringIO()
        req = ApacheRequestMockup('foobar', fin, fout)

        rslt = jsonrpc.handler(req)
        self.assertEqual(rslt, 'OK')
        data = fout.getvalue()

        expect = {'id': '', 'error': {'message': 'Method not found', 'code': -32601}}
        actual = jsonrpc.loads(data)
        self.assertEqual(expect, actual)

    def test_service_echoes_unicode(self):
        echo_data = {'hello': uchr(0x1234)}
        json = jsonrpc.dumps({'id': '', 'params': [echo_data], 'method': 'echo'})

        fin = StringIO(json)
        fout = StringIO()
        req = ApacheRequestMockup(__file__, fin, fout)

        result = jsonrpc.handler(req)
        self.assertEqual(result, 'OK')
        data = fout.getvalue()

        expect = echo_data
        actual = jsonrpc.loads(data)['result']

        self.assertEqual(expect, actual)
