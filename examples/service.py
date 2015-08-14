#!/usr/bin/env python
import os
import sys

# Find the source tree
service_py = os.path.abspath(__file__)
jsonrpc_src = os.path.dirname(os.path.dirname(service_py))
if jsonrpc_src not in sys.path:
    sys.path.insert(1, jsonrpc_src)

from jsonrpc import handleCGI, servicemethod
from jsonrpc import servicemodule
from jsonrpc import servicechain

import servicemodule_example


# The json-rpc mod_python handler automatically makes a web service
# out of a class called Service.

class Echo(object):
    @servicemethod
    def echo(self, *args, **kwargs):
        """Return what is passed in"""
        return args or kwargs or None

class Add(object):
    @servicemethod
    def add(self, a, b):
        return a + b


def get_service():
    add = Add()
    echo = Echo()
    module = servicemodule(servicemodule_example)
    # Expose functions from multiple sources as a single service
    return servicechain(add, echo, module)

if __name__ == '__main__':
    service = get_service()
    handleCGI(service)
