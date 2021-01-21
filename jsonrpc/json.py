from __future__ import absolute_import, division, unicode_literals
from datetime import datetime

try:
    json = __import__('simplejson')
except ImportError:
    json = __import__('json')


loads = json.loads

JSONEncodeException = TypeError
JSONDecodeException = ValueError


def dumps(*args, **opts):
    """Dumps JSON using the custom JSON-RPC object handler"""
    opts.setdefault('default', _handler)
    return json.dumps(*args, **opts)


def _handler(obj):
    """JSON callback used for unknown types

    Converts datetime objects to ISO-formatted strings via datetime.isoformat().

    """
    if isinstance(obj, datetime) and hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(repr(obj) + ' is not JSON serializable')
