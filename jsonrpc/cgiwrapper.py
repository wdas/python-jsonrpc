import os
import sys

from . import ServiceHandler


class CGIServiceHandler(ServiceHandler):
    def __init__(self, service, tracebacks=False):
        if service is None:
            import __main__ as service
        super(CGIServiceHandler, self).__init__(service, tracebacks=tracebacks)

    def handle_request(self, fin=None, fout=None, env=None):
        if fin is None:
            fin = sys.stdin
        if fout is None:
            fout = sys.stdout
        if env is None:
            env = os.environ
        try:
            content_length = int(env['CONTENT_LENGTH'])
            data = fin.read(content_length)
        except (KeyError, ValueError):
            data = fin.read()

        result = super(CGIServiceHandler, self).handle_request(data)

        response = 'Content-Type: application/json\n'
        response += 'Content-Length: %d\n\n' % len(result)
        response += result

        # on windows all \n are converted to \r\n if stdout is a terminal and
        # is not set to binary mode :(
        # this will then cause an incorrect Content-length.
        # I have only experienced this problem with apache on Win so far.
        if sys.platform == 'win32':
            try:
                import msvcrt

                msvcrt.setmode(fout.fileno(), os.O_BINARY)
            except (ImportError, Exception):
                pass
        # put out the response
        fout.write(response)
        fout.flush()


def handleCGI(service=None, fin=None, fout=None, env=None, tracebacks=False):
    CGIServiceHandler(service, tracebacks=tracebacks).handle_request(fin, fout, env)
