
"""
  Copyright (c) 2007 Jan-Klaas Kollhof

  This file is part of jsonrpc.

  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

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
