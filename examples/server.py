#!/usr/bin/python

import os
import signal
import optparse
import urlparse

import BaseHTTPServer
import CGIHTTPServer
import cgitb

DEFAULT_URL = 'http://localhost:8080/service.py'


def main():
    parser = optparse.OptionParser()
    parser.add_option('-u', '--url', metavar='URL',
                      help='Service URL (default: %s)' % DEFAULT_URL,
                      default=DEFAULT_URL)
    opts, args = parser.parse_args()

    url = urlparse.urlparse(opts.url)
    hostname = url.hostname
    port = url.port or 80

    server = BaseHTTPServer.HTTPServer
    handler = CGIHTTPServer.CGIHTTPRequestHandler
    server_address = (hostname, port)
    service_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(service_dir)
    handler.cgi_directories = ['/', '']

    print('JSON-RPC echo server')
    print('Serving %s to http://%s:%s' % (service_dir, hostname, port))
    print('API at %s' % (opts.url,))
    print('-------------------------------------------')

    signal.signal(signal.SIGINT, signal.SIG_DFL) ## Silence Ctrl-C
    cgitb.enable()  ## Enables CGI error reporting
    httpd = server(server_address, handler)
    httpd.serve_forever()


if '__main__' == __name__:
    main()
