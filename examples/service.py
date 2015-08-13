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

import servicemodule_example


def get_item(obj, name):
    if hasattr(obj, '__getitem__'):
        return obj[name]
    else:
        return getattr(obj, name)


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


class Group(object):
    """Proxy over a group of objects"""

    def __init__(self, *members):
        self._members = members

    def __getattr__(self, name):
        err = None
        for m in self._members:
            try:
                attr = get_item(m, name)
                setattr(self, name, attr)
                return attr
            except (KeyError, AttributeError) as e:
                err = e
        # No attribute was found so raise the original exception
        if not err:
            err = AttributeError(name)
        raise err


if __name__ == '__main__':
    # Handle CGI
    add = Add()
    echo = Echo()
    module = servicemodule(servicemodule_example)
    # Expose functions from multiple sources as a single service
    service = Group(add, echo, module)
    handleCGI(service)
