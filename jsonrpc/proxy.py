"""
  Copyright (C) 2007 Jan-Klaas Kollhof
  Copyright (C) 2012 David Aguilar

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
         if resp['error'] is not None:
             raise JSONRPCException(resp['error'])
         else:
             return resp['result']
