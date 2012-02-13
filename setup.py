#!/usr/bin/env python

from distutils.core import setup
import jsonrpc

setup(name = 'jsonrpc',
      version = jsonrpc.__version__,
      description = 'A json-rpc package which implements JSON-RPC over HTTP.',
      keywords = 'JSON RPC',
      author = 'David Aguilar',
      url = 'https://github.com/davvid/python-jsonrpc',
      license = 'LGPL',
      long_description = """""",
      packages = ['jsonrpc']
)
