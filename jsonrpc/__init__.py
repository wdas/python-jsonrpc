__version__ = '2.0'

from jsonrpc.json import loads, dumps, JSONEncodeException, JSONDecodeException
from jsonrpc.proxy import ServiceProxy, JSONRPCException
from jsonrpc.servicehandler import servicemethod, ServiceHandler, ServiceMethodNotFound, ServiceException
from jsonrpc.cgiwrapper import handleCGI
from jsonrpc.modpywrapper import handler

from jsonrpc.servicehandler import servicemodule

# Backwards compatibility: remove in v2.1
from jsonrpc.servicehandler import servicemethod as ServiceMethod
