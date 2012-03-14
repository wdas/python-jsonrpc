#!/usr/bin/env python
import os
import sys

# Find the source tree
service_py = os.path.abspath(__file__)
jsonrpc_src = os.path.dirname(os.path.dirname(service_py))
if jsonrpc_src not in sys.path:
    sys.path.insert(1, jsonrpc_src)

from jsonrpc import handleCGI, servicemethod

# The json-rpc mod_python handler automatically makes a web service
# out of a class called Service.

class Service(object):
    @servicemethod
    def echo(self, *args, **kwargs):
        """Return what is passed in"""
        return args or kwargs or None

    @servicemethod
    def add(self, a, b):
        return a + b


if __name__ == '__main__':
    # Handle CGI
    service = Service()
    handleCGI(service)
