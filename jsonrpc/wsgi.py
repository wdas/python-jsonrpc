from jsonrpc import ServiceHandler


class WsgiServiceHandler(ServiceHandler):

    def __init__(self, service=None, tracebacks=False):
        if service is None:
            import __main__ as service
        super(WsgiServiceHandler, self).__init__(service, tracebacks=tracebacks)

    def handle_request(self, environ, start_response):
        data = environ['wsgi.input'].read()
        result = super(WsgiServiceHandler, self).handle_request(data)
        start_response('200 OK',
                       [('Content-Type', 'application/json'),
                        ('Content-Length', '%d' % len(result))])
        return [result]
