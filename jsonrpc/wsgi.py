from __future__ import absolute_import, division, unicode_literals

from jsonrpc import ServiceHandler


class WsgiServiceHandler(ServiceHandler):
    def __init__(self, service=None, tracebacks=False):
        if service is None:
            import __main__ as service
        super(WsgiServiceHandler, self).__init__(service, tracebacks=tracebacks)

    def handle_request(self, env, start_response):
        content_length = int(env.get('CONTENT_LENGTH', 0))
        content_reader = WsgiContentReader(env['wsgi.input'], content_length)
        data = content_reader.read_data()
        result = super(WsgiServiceHandler, self).handle_request(data)
        start_response(
            '200 OK',
            [
                ('Content-Type', 'application/json'),
                ('Content-Length', '%d' % len(result)),
            ],
        )
        return [result]


class WsgiContentReader(object):
    def __init__(self, fp, content_length, chunk_size=4096):
        self.fp = fp
        self.content_length = content_length
        self.chunk_size = chunk_size

    def read_data(self):
        result = ''
        if self.content_length == 0:
            return result

        for chunk in self._read():
            result += chunk
        return result

    def _read(self):
        bytes_read = 0
        size = self.chunk_size

        while bytes_read < self.content_length:
            remaining = self.content_length - bytes_read
            if remaining < self.chunk_size:
                size = remaining
            data = self.fp.read(size)
            bytes_read += len(data)
            yield data
