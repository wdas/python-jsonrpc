import sys

import http.client as httplib  # noqa: F401
from io import StringIO  # noqa: F401


def decode(string):
    """Decode a string to bytes"""
    if isinstance(string, bytes):
        result = string.decode('utf-8', errors='ignore')
    else:
        result = string
    return result


def encode(string):
    """Encode a string to bytes"""
    if isinstance(string, str):
        result = string.encode('utf-8', errors='ignore')
    else:
        result = string
    return result
