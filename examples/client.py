#!/usr/bin/python

import os
import sys
import code
import optparse
import readline
import rlcompleter

client_py = os.path.abspath(__file__)
sys.path.insert(1, os.path.dirname(os.path.dirname(client_py)))

from jsonrpc import ServiceProxy
from jsonrpc.proxy import JSONRPCException

from server import DEFAULT_URL


class ServerError(StandardError):
    def __init__(self, details):
        self.details = details
        self.name = self.details.get('name', 'UnknownServerError')
        self.msg = self.details.get('message', '')
        self.traceback = self.details.get('traceback', '')
        super(ServerError, self).__init__('%s: %s' % (self.name, self.msg))

    def __str__(self):
        if self.traceback:
            return self.traceback
        return super(StandardError, self).__str__()


class Client(object):
    def __init__(self, url):
        self.internal_proxy_obj = ServiceProxy(url)

    def __getattr__(self, attr):
        def attr_wrapper(*args, **kwargs):
            proxy_attr = getattr(self.internal_proxy_obj, attr)
            try:
                return proxy_attr(*args, **kwargs)
            except JSONRPCException as e:
                raise ServerError(e.error)

        setattr(self, attr, attr_wrapper)
        return attr_wrapper


def main():
    parser = optparse.OptionParser()
    parser.add_option(
        '-u',
        '--url',
        metavar='URL',
        help='Service URL (default: %s)' % DEFAULT_URL,
        default=DEFAULT_URL,
    )
    opts, args = parser.parse_args()

    client = Client(opts.url)
    namespace = {
        'client': client,
        'c': client,
    }

    readline.parse_and_bind('tab: complete')
    shell = code.InteractiveConsole(namespace)

    banner = [
        'JSON-RPC Python Console',
        'Connected to %s' % opts.url,
        '',
        'Example usage:',
        '\tclient.add(1, 2)',
        '\tclient.echo("Hello, world")',
        '',
    ]

    return shell.interact('\n'.join(banner))


if __name__ == '__main__':
    main()
