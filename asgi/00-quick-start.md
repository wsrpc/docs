# FastAPI browser demo

For the shared RPC walkthrough with framework tabs, see the
[quick start](../quick-start.md).

Install the server framework and optional Python client:

```shell
pip install 'wsrpc-asgi[fastapi,client]' uvicorn
```

## FastAPI and a browser

The complete server is in [examples/main/server.py](examples/main/server.py).
It exposes `uuid4`, serves the bundled JavaScript client and a browser page.
Static paths are resolved relative to the example file, so the server does
not depend on the current directory.

```{literalinclude} examples/main/server.py
:language: python
```

From this documentation checkout, after installing the ASGI library and FastAPI
(see the [framework guide](../contributing.md#check-asgi-integrations-locally)):

```shell
uv run --no-sync python asgi/examples/main/server.py
```

Open <http://127.0.0.1:8000/web-client.html>. The browser connects to `/ws/`
and requests a UUID. Its source is:

```{literalinclude} examples/main/web-client.html
:language: html
```

## Python client

In another terminal run:

```shell
uv run --no-sync python asgi/examples/main/client.py
```

```{literalinclude} examples/main/client.py
:language: python
```

A peer can also expose callbacks. The larger
[server demo](examples/server.py) calls the Python client's `joke` route.
Run the server and client in separate terminals:

```shell
uv run --no-sync python asgi/examples/server.py
uv run --no-sync python asgi/examples/client.py
```

For Starlette, Django, Channels, Quart, Litestar, Falcon, Sanic, BlackSheep
or a standalone endpoint see [framework integrations](frameworks.md).
