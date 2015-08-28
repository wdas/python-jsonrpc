import os
import sys

examples = os.path.dirname(os.path.abspath(__file__))
jsonrpc = os.path.dirname(examples)
module_dirs = (jsonrpc, examples)
sys.path.extend(module_dirs)

from jsonrpc.wsgi import WsgiServiceHandler

import service

_service = service.get_service()
_handler = WsgiServiceHandler(_service)


def application(environ, start_response):
    return _handler.handle_request(environ, start_response)
