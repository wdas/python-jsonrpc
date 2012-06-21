from datetime import datetime

try:
    json = __import__('simplejson')
except ImportError:
    json = __import__('json')

loads = json.loads

JSONEncodeException = TypeError
JSONDecodeException = ValueError


def dumps(*args, **opts):
    if 'default' not in opts:
        opts['default'] = _handler
    return json.dumps(*args, **opts)


def _handler(obj):
    """Convert datetime objects to ISO date strings"""
    if isinstance(obj, datetime) and hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return json.dumps(obj)
