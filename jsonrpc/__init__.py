# flake8: ignore=F401
from __future__ import absolute_import, division, unicode_literals

from .json import loads, dumps, JSONEncodeException, JSONDecodeException
from .proxy import ServiceProxy, JSONRPCException
from .servicehandler import (
    servicemethod,
    ServiceHandler,
    ServiceMethodNotFound,
    ServiceException,
)
from .cgiwrapper import handleCGI
from .modpywrapper import handler

from .servicehandler import servicechain
from .servicehandler import servicemodule

# Backwards compatibility: remove in v2.1
from .servicehandler import servicemethod as ServiceMethod


__version__ = '2.1'
__all__ = (
    # jsonrpc
    'handler',
    'handleCGI',
    'JSONDecodeException',
    'JSONEncodeException',
    'JSONRPCException',
    'servicechain',
    'servicehandler',
    'servicemethod',
    'servicemodule',
    'ServiceException',
    'ServiceHandler',
    'ServiceMethodNotFound',
    'ServiceProxy',
    # json wrappers
    'loads',
    'dumps',
    # Backwards compatibility
    'ServiceMethod',
)
