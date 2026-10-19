# Framework integrations

All examples expose the same RPC methods at `ws://127.0.0.1:8000/ws/`:
`echo` returns its keyword arguments; `callback` calls the client's `double`
method. Framework applications also expose an ordinary HTTP `/health` route.

The RPC routes used below are defined once:

```{literalinclude} examples/frameworks/common.py
:language: python
```

## Run the examples

From the documentation checkout, install the example frameworks and your
local ASGI library checkout:

```shell
uv sync --group integrations
uv pip install --python .venv/bin/python -e ../wsrpc-asgi
uv run --no-sync --group integrations uvicorn asgi.examples.frameworks.fastapi_app:app
```

Replace `fastapi_app` with a module in the table below. These working
source files are included in the documentation checkout; copy them into your own
package and adjust the relative import of `common` when adapting an example.
The editable install above assumes a sibling `../wsrpc-asgi` checkout.
For an installed application, install the ASGI library distribution, your
framework and an ASGI server instead. The documentation build itself does
not require the ASGI library or the optional frameworks.

| Integration | Module suffix | Framework dependency |
| --- | --- | --- |
| FastAPI | `fastapi_app` | `fastapi` |
| Starlette | `starlette_app` | `starlette` |
| Django | `django_app` | `django` |
| Django Channels | `channels_app` | `django`, `channels` |
| Quart | `quart_app` | `quart` |
| Litestar | `litestar_app` | `litestar` |
| Falcon | `falcon_app` | `falcon` |
| Sanic in ASGI mode | `sanic_app` | `sanic` |
| BlackSheep | `blacksheep_app` | `blacksheep` |
| Bare ASGI | `bare_app` | none |

With any example running, try the same client:

```python
import asyncio
from wsrpc_asgi import WSRPCClient


async def main():
    async with WSRPCClient("ws://127.0.0.1:8000/ws/") as client:
        client.add_route("double", lambda socket, value: value * 2)
        print(await client.proxy.echo(message="Hello"))
        print(await client.proxy.callback(value=21))


if __name__ == "__main__":
    asyncio.run(main())
```

## FastAPI

Use a normal WebSocket endpoint to retain FastAPI's dependencies and router
middleware. `serve()` accepts the socket itself. Pass dependency results via
`context`; RPC route code reads them through `self.socket.context` or
`socket.context` for function routes. Dependencies are scoped to the connection,
not re-evaluated for each RPC message.

```{literalinclude} examples/frameworks/fastapi_app.py
:language: python
```

`serve()` owns acceptance and closure: pass an unaccepted WebSocket.
For cookie/header authentication use a dependency or override `authorize()`.
When using `serve()` directly, registrations and the client collection belong
to the handler class. Define a separate subclass for each application.

[FastAPI WebSocket documentation](https://fastapi.tiangolo.com/advanced/websockets/).

## Starlette

An ASGI endpoint can be installed directly in a `WebSocketRoute`. Keep the
returned `RPCApplication` to broadcast to its clients and explicitly close
it in the parent application's lifespan. The endpoint owns an isolated
snapshot of its handler's routes and signals.

```{literalinclude} examples/frameworks/starlette_app.py
:language: python
```

[Starlette routing](https://www.starlette.dev/routing/).

## Django

Wrap Django's ASGI application with `RPCMiddleware`. Django continues to
serve HTTP; the wrapper handles the selected WebSocket path. The example
provides minimal standalone settings. In a real project retain your generated
`asgi.py`, `DJANGO_SETTINGS_MODULE` and application settings.

```{literalinclude} examples/frameworks/django_app.py
:language: python
```

The wrapper does not apply Django's HTTP middleware to RPC connections.
Implement WebSocket authorization separately. Use Django's async ORM or
`sync_to_async` when calling synchronous Django APIs from RPC handlers.

[Django ASGI deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/).

## Django Channels

Install the endpoint in `URLRouter` under `ProtocolTypeRouter`. Channels
middleware can populate `scope`, which RPC handlers can read through
`socket.scope`. For session authentication, wrap the WebSocket router with
`AuthMiddlewareStack` and the appropriate origin validator in your configured
Django project; the standalone example has no user/session authentication.

```{literalinclude} examples/frameworks/channels_app.py
:language: python
```

## Quart

Wrap `app.asgi_app`, preserving the Quart application object and its API.

```{literalinclude} examples/frameworks/quart_app.py
:language: python
```

[Quart middleware](https://quart.palletsprojects.com/en/latest/how_to_guides/middleware/).

## Litestar

```{literalinclude} examples/frameworks/litestar_app.py
:language: python
```

The wrapper forwards HTTP and lifecycle messages to Litestar and routes the
RPC WebSocket before Litestar's own routing.

[Litestar applications](https://docs.litestar.dev/main/usage/applications.html).

## Falcon

Use `falcon.asgi.App`, its asynchronous application class.

```{literalinclude} examples/frameworks/falcon_app.py
:language: python
```

[Falcon ASGI tutorial](https://falcon.readthedocs.io/en/latest/user/tutorial-asgi.html).

## Sanic

Run the wrapped application with an ASGI server, rather than Sanic's native
server, so the RPC wrapper receives connections.

```{literalinclude} examples/frameworks/sanic_app.py
:language: python
```

[Sanic deployment](https://sanic.dev/en/guide/running/running.md).

## BlackSheep

```{literalinclude} examples/frameworks/blacksheep_app.py
:language: python
```

[BlackSheep ASGI](https://www.neoteroi.dev/blacksheep/asgi/).

## Bare ASGI and other frameworks

```{literalinclude} examples/frameworks/bare_app.py
:language: python
```

`as_asgi()` implements the `(scope, receive, send)` interface directly.
Use it as a framework's ASGI route, or compose an existing ASGI app:

```python
from wsrpc_asgi import RPCMiddleware, WebSocketAsync


class RPC(WebSocketAsync):
    pass


rpc = RPC.as_asgi()
# existing_app is your framework's ASGI callable.
# app = RPCMiddleware(existing_app, rpc, path="/ws/")
```

The wrapper forwards unmatched HTTP/WebSocket scopes without modifying them.
Its RPC path is matched exactly, including the trailing slash. Routing inside
a mounted framework should normally use `as_asgi()` without a path restriction
and let that framework select the route.

Framework middleware *inside* `RPCMiddleware` does not run on the RPC path.
Place shared ASGI authentication outside the wrapper or implement
`authorize()`. HTTP CORS middleware is not WebSocket origin authorization.

## Lifecycle and servers

Standalone endpoints handle ASGI startup and shutdown. Framework routers
generally do not forward lifespan messages to mounted endpoints; call
`await rpc.close()` in the parent lifespan, as the Starlette example does.
`RPCMiddleware` forwards the parent's lifespan and closes RPC sessions before
passing its shutdown event onward. Django/Channels without lifespan support
still clean up each connection on disconnect.

All integrations require an **asyncio** server backend. Uvicorn:

```shell
uv run --no-sync --group integrations uvicorn asgi.examples.frameworks.fastapi_app:app --host 127.0.0.1 --port 8000
```

Hypercorn:

```shell
uv run --no-sync --group integrations hypercorn asgi.examples.frameworks.fastapi_app:app --worker-class asyncio --bind 127.0.0.1:8000
```

Other ASGI servers can serve the same callable when configured for asyncio
and WebSocket support. WebSocket protocol PING/PONG is the server's concern;
WSRPC's application-level `ping` route remains available independently.

Broadcast and connection state are local to a worker process. With multiple
workers, distribute application events yourself when every worker must see
them. The library does not introduce a broker or shared session storage.
