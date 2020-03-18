import unittest

import jsonrpc
from jsonrpc.compat import StringIO


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg


class  TestCGIWrapper(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handleCGI(self):
        json = '{"method":"echo","params":["foobar"], "id":""}'
        fin = StringIO(json)
        fout = StringIO()

        env = {'CONTENT_LENGTH': len(json)}

        jsonrpc.handleCGI(service=Service(), fin=fin, fout=fout, env=env)

        data = StringIO(fout.getvalue())
        data.readline()
        data.readline()
        data = data.read()
        expect = {'result':'foobar', 'jsonrpc': '2.0', 'id':''}
        actual = jsonrpc.loads(data)
        self.assertEqual(expect, actual)
