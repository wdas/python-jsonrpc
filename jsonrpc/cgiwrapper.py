import sys, os
from jsonrpc import ServiceHandler

class CGIServiceHandler(ServiceHandler):
    def __init__(self, service):
        if service is None:
            import __main__ as service
        super(CGIServiceHandler, self).__init__(service)

    def handle_request(self, fin=None, fout=None, env=None):
        if fin is None:
            fin = sys.stdin
        if fout is None:
            fout = sys.stdout
        if env == None:
            env = os.environ
        try:
            content_length = int(env['CONTENT_LENGTH'])
            data = fin.read(content_length)
        except Exception:
            data = ''

        result = super(CGIServiceHandler, self).handle_request(data)

        response = 'Content-Type: text/plain\n'
        response += 'Content-Length: %d\n\n' % len(result)
        response += result

        #on windows all \n are converted to \r\n if stdout is a terminal and  is not set to binary mode :(
        #this will then cause an incorrect Content-length.
        #I have only experienced this problem with apache on Win so far.
        if sys.platform == 'win32':
            try:
                import  msvcrt
                msvcrt.setmode(fout.fileno(), os.O_BINARY)
            except:
                pass
        #put out the response
        fout.write(response)
        fout.flush()


def handleCGI(service=None, fin=None, fout=None, env=None):
    CGIServiceHandler(service).handle_request(fin, fout, env)
