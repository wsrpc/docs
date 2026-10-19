# ASGI integration details

For runnable installation and server examples, choose a framework tab in the
[shared quick start](../quick-start.md). This page covers integration-specific
authentication, lifecycle and deployment behavior.

## FastAPI

Use a normal WebSocket endpoint to retain FastAPI's dependencies and router
middleware. `serve()` accepts the socket itself. Pass dependency results via
`context`; RPC route code reads them through `self.socket.context` or
`socket.context` for function routes. Dependencies are scoped to the connection,
not re-evaluated for each RPC message.

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

[Starlette routing](https://www.starlette.dev/routing/).

## Django

Wrap Django's ASGI application with `RPCMiddleware`. Django continues to
serve HTTP; the wrapper handles the selected WebSocket path. The example
provides minimal standalone settings. In a real project retain your generated
`asgi.py`, `DJANGO_SETTINGS_MODULE` and application settings.

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

## Quart

Wrap `app.asgi_app`, preserving the Quart application object and its API.

[Quart middleware](https://quart.palletsprojects.com/en/latest/how_to_guides/middleware/).

## Litestar

The wrapper forwards HTTP and lifecycle messages to Litestar and routes the
RPC WebSocket before Litestar's own routing.

[Litestar applications](https://docs.litestar.dev/main/usage/applications.html).

## Falcon

Use `falcon.asgi.App`, its asynchronous application class.

[Falcon ASGI tutorial](https://falcon.readthedocs.io/en/latest/user/tutorial-asgi.html).

## Sanic

Run the wrapped application with an ASGI server, rather than Sanic's native
server, so the RPC wrapper receives connections.

[Sanic deployment](https://sanic.dev/en/guide/running/running.md).

## BlackSheep

[BlackSheep ASGI](https://www.neoteroi.dev/blacksheep/asgi/).

## Bare ASGI and other frameworks

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
`await rpc.close()` in the parent lifespan, as the Starlette tab in the quick start does.
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
