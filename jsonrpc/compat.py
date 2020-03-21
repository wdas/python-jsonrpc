try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    import http.client as httplib
except ImportError:
    import httplib
