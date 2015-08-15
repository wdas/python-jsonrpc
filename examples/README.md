JSON-RPC Examples
=================
This directory contains an example server, client, and
python service module.

WSGI
----
`app.wsgi` is an example wsgi service file for use with with WSGI containers.

Nginx
~~~~~
The Nginx example consists of two parts: nginx and uwsgi.
This approach runs the uwsgi application using `uwsgi`, exposes a socket,
and uses nginx as a proxy.

See the nginx/ and uwsgi/ directories for configuration examples.

Apache
~~~~~~
The apache2/ directory contains an example Apache `mod_wsgi` configuration.

We also provide an older `mod_python`-based service handler in the
`jsonrpc.modpywrapper` module, but using wsgi is recommended if possible.


Example Python Server
---------------------

Usage
~~~~~

Start the example JSON-RPC CGI Server:

    python server.py

This starts an HTTP server listening on port 8080.
It exposes the methods provided by the `Service` class in `service.py`.
To test the service you can run the example client:

    python client.py

This starts a Python console with a connected `client` object.
You can invoke RPC methods interactively by using the `client` object.

`client.py` can connect to any JSON-RPC server.
Alternative service URLs are specified using the `--url` option.

Low-level HTTP Requests
~~~~~~~~~~~~~~~~~~~~~~~

You can issue JSON-RPC requests against the example server using `curl`.

    data='{"jsonrpc":"2.0", "id":null, "method":"add", "params":[1,2]}'
    curl --data "$data" http://localhost:8080/service.py


Low-level CGI Execution
~~~~~~~~~~~~~~~~~~~~~~~

You can invoke the `service.py` CGI handler directly using this trick
in case you're curious about how CGI works.

    data='{"jsonrpc":"2.0", "id":null, "method":"add", "params":[1,2]}'
    echo -n "$data" |
    CONTENT_TYPE=application/json \
    CONTENT_LENGTH=$(python -c "print(len('$data'))") \
    python service.py
