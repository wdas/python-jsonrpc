import unittest
import jsonrpc


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg


class ApacheRequestMockup(object):
    def __init__(self, filename, fin, fout):
        self.fin = fin
        self.fout = fout
        self.filename = filename

    def write(self,data):
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


class  TestModPyWrapper(unittest.TestCase):
    def setUp(self):
        import sys
        sys.modules['mod_python'] = ModPyMockup()

    def tearDown(self):
        pass

    def test_mod_python_handler(self):
        from StringIO import StringIO

        json=u'{"method":"echo","params":["foobar"], "id":""}'
        fin=StringIO(json)
        fout=StringIO()
        req = ApacheRequestMockup(__file__ , fin, fout)

        jsonrpc.handler(req)

        data = fout.getvalue()

        self.assertEquals(jsonrpc.loads(data),
                          {'result': 'foobar',
                           'error': None,
                           'id': ''})

    def test_service_implementation_not_found(self):
        from StringIO import StringIO

        json=u'{"method":"echo","params":["foobar"], "id":""}'
        fin=StringIO(json)
        fout=StringIO()
        req = ApacheRequestMockup('foobar', fin, fout)

        rslt = jsonrpc.handler(req)
        self.assertEquals(rslt, 'OK')
        data = fout.getvalue()

        self.assertEquals(jsonrpc.loads(data),
                          {u'id': '',
                           u'result': None,
                           u'error': {
                               u'message': '',
                               u'name': u'ServiceImplementaionNotFound'}})
