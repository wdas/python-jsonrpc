from __future__ import absolute_import, division, unicode_literals
import unittest

import jsonrpc
from io import BytesIO


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg


class TestCGIWrapper(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handleCGI(self):
        json = b'{"method":"echo","params":["foobar"], "id":""}'
        fin = BytesIO(json)
        fout = BytesIO()

        env = {'CONTENT_LENGTH': len(json)}

        jsonrpc.handleCGI(service=Service(), fin=fin, fout=fout, env=env)

        data = BytesIO(fout.getvalue())
        data.readline()
        data.readline()
        data = data.read()
        expect = {'result': 'foobar', 'jsonrpc': '2.0', 'id': ''}
        actual = jsonrpc.loads(data)
        self.assertEqual(expect, actual)
