import sys, os
from jsonrpc import ServiceHandler, ServiceException


class ServiceImplementaionNotFound(ServiceException):
    pass


class ModPyServiceHandler(ServiceHandler):
    def __init__(self, req):
        self.req = req
        super(ModPyServiceHandler, self).__init__(None)

    def find_service_method(self, name):
        req = self.req

        (path, filename) = os.path.split(req.filename)
        (module, ext) = os.path.splitext(filename)

        if not os.path.exists(os.path.join(path, module +'.py')):
            raise ServiceImplementaionNotFound()
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


def handler(req):
    from mod_python import apache
    ModPyServiceHandler(req).handle_request(req)
    return apache.OK
