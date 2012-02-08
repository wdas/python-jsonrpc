import unittest
import jsonrpc


class Service(object):
    @jsonrpc.servicemethod
    def echo(self, arg):
        return arg


class  TestCGIWrapper(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_runCGIHandler(self):
        from StringIO import StringIO

        json=u'{"method":"echo","params":["foobar"], "id":""}'
        fin=StringIO(json)
        fout=StringIO()

        env = {"CONTENT_LENGTH":len(json)}

        jsonrpc.handleCGI(service=Service(), fin=fin, fout=fout, env=env)

        data = StringIO(fout.getvalue())
        data.readline()
        data.readline()
        data = data.read()
        self.assertEquals(jsonrpc.loads(data),
                          {"result":"foobar",
                           "error":None,
                           "id":""})
