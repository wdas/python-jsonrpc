import sys, os
from jsonrpc import ServiceHandler, ServiceException


class ServiceMethodNotFound(ServiceException):
    jsonrpc_error_code = -32601
    jsonrpc_error_msg = 'Method not found'


class ModPyServiceHandler(ServiceHandler):
    def __init__(self, req, tracebacks=False):
        super(ModPyServiceHandler, self).__init__(None, tracebacks=tracebacks)
        self.req = req

    def find_service_method(self, name):
        req = self.req

        (path, filename) = os.path.split(req.filename)
        (module, ext) = os.path.splitext(filename)

        if not os.path.exists(os.path.join(path, module +'.py')):
            raise ServiceMethodNotFound()
        else:
            if not path in sys.path:
                sys.path.insert(1, path)

            from mod_python import apache
            module = apache.import_module(module, log=1)

            if hasattr(module, 'service'):
                self.service = module.service
            elif hasattr(module, 'Service'):
                self.service = module.Service()
            else:
                self.service = module

        return super(ModPyServiceHandler, self).find_service_method(name)

    def handle_request(self, data):
        self.req.content_type = 'application/json'
        data = self.req.read()
        result = super(ModPyServiceHandler, self).handle_request(data)
        self.req.write(result)
        self.req.flush()


def handler(req, tracebacks=False):
    from mod_python import apache
    ModPyServiceHandler(req, tracebacks=tracebacks).handle_request(req)
    return apache.OK
