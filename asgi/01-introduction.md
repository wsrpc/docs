# Routes and connections

## Function routes

Register routes before creating an ASGI endpoint. Function handlers receive
the RPC connection as their first argument. A route can be synchronous or
asynchronous:

<!-- name: test_routes -->
```python
from wsrpc_asgi import WebSocketAsync


class RPC(WebSocketAsync):
    pass


async def echo(socket, **params):
    return params


RPC.add_route("echo", echo)
app = RPC.as_asgi()
```

`WebSocketAsync` runs synchronous functions on the event loop. Use
`WebSocketThreaded` for blocking synchronous handlers; coroutine handlers
still run on the event loop. Cancelling a threaded call cannot stop Python
code that is already running in a thread, so such code must arrange its own
cooperative cancellation when necessary.

## Connection-scoped routes

A route object is created lazily once for each connection. Calling the bare
route name resolves `init`; `init` is **not** called automatically before
other methods.

```python
from wsrpc_asgi import WebSocketAsync, WebSocketRoute, decorators


class Counter(WebSocketRoute[WebSocketAsync]):
    def init(self, value: int = 0):
        self.value = value

    def increment(self, amount: int = 1):
        self.value += amount
        return self.value

    @decorators.noproxy
    def private(self):
        return "not remotely accessible"

    async def _onclose(self):
        # Release this route's resources. Cleanup is awaited.
        pass


class RPC(WebSocketAsync):
    pass


RPC.add_route("counter", Counter)
app = RPC.as_asgi()
```

A client first calls `await client.proxy.counter(value=10)` and then
`await client.proxy.counter.increment(amount=2)`.

| Route class | Exposed methods |
| --- | --- |
| `Route` | Methods marked with `@decorators.proxy` |
| `AllowedRoute` / `WebSocketRoute` | Public methods, unless masked |
| `PrefixRoute` | Methods prefixed with `rpc_`; callers omit the prefix |

Private names beginning with `_` are masked. `@decorators.noproxy` masks a
method explicitly, including inherited methods.

## Reverse calls and events

Either peer can call the other while handling an incoming request:

```python
async def ask_client(socket, *, value):
    return await socket.proxy.double(value=value)
```

Register `double` on the Python or JavaScript client. The read loop continues
processing replies while the request handler waits for this callback.

Use `await socket.emit({"event": "changed", "value": 42})` for an event
without a response. Register a synchronous event callback with
`client.add_event_listener(callback)`; remove it with
`client.remove_event_listeners(callback)`. Event objects must omit `id`.

## Python and JavaScript clients

Install `wsrpc-asgi[client]` for the Python peer:

```python
import asyncio
from wsrpc_asgi import WSRPCClient


async def main():
    async with WSRPCClient("ws://127.0.0.1:8000/ws/", timeout=5) as client:
        client.add_route("double", lambda socket, value: value * 2)
        result = await client.call("echo", message="Hello")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

Additional client constructor keywords go to
`websockets.asyncio.client.connect`, for example `additional_headers`,
`ssl` and `open_timeout`. `http://` and `https://` endpoints are also accepted
and converted to their WebSocket equivalents. The context manager closes the
connection; a closed client cannot be reconnected. Create a new client for a
new session. A failed handshake can be retried before the client is closed.

The bundled browser client uses the unchanged WSRPC protocol:

```javascript
const rpc = new WSRPC("ws://127.0.0.1:8000/ws/");
rpc.addRoute("double", ({ value }) => value * 2);
rpc.connect();
await rpc.onEvent("onconnect");
try {
    console.log(await rpc.call("echo", { message: "Hello" }));
} catch (error) {
    console.error(error);
}
```

Load `wsrpc.min.js` as a classic script or import `wsrpc.es6.js` as a module.
`STATIC_DIR` points to the installed assets; serve them through your framework's
static file support or copy them into your frontend distribution.

## Configuration and limits

`RPC.configure()` accepts `keepalive_timeout`, `client_timeout`,
`max_concurrent_requests`, `loads` and `dumps`. Configure before creating the
ASGI application. Further settings can be overridden on a handler subclass:

```python
from wsrpc_asgi import WebSocketAsync


class RPC(WebSocketAsync):
    MAX_CONCURRENT_REQUESTS = 25
    MAX_PENDING_REQUESTS = 1024
    REQUEST_EXECUTION_TIMEOUT = 10
    KEEPALIVE_PING_TIMEOUT = 30
    CLIENT_TIMEOUT = 10
```

`MAX_PENDING_REQUESTS` bounds outstanding incoming requests, including those
waiting for an execution slot. Excess requests receive an RPC error. Replies
to outgoing calls do not consume execution slots. Set server-level WebSocket
message-size and transport queue limits in Uvicorn or Hypercorn as well.

`REQUEST_EXECUTION_TIMEOUT` limits a handler's execution and is also the
default timeout for server-to-client calls. `client.call(..., timeout=...)`
overrides that call's timeout. Timeout and cancellation remove pending local
futures; they do not send a cancellation message to the remote peer. Late
responses are ignored. Disconnect fails pending calls with `ConnectionError`.

`KEEPALIVE_PING_TIMEOUT` controls the interval between RPC `ping` calls;
`CLIENT_TIMEOUT` controls how long each reply may take. Set the interval to
zero to disable application-level keepalive.

## JSON and custom serialization

Standard-library `json` is the default. Pass your own compatible `loads` and
`dumps` explicitly; the library does not select a native codec automatically.
`dumps` must return `str` and accept `default=serializer`.

```python
import json
from wsrpc_asgi import WebSocketAsync, serializer


class RPC(WebSocketAsync):
    pass


RPC.configure(loads=json.loads, dumps=json.dumps)


class Point:
    def __init__(self, x: int):
        self.x = x


@serializer.register(Point)
def serialize_point(value: Point):
    return {"x": value.x}
```

Bytes inside JSON values are base64-encoded by `serializer`. Raw binary
WebSocket messages are separate: override `async def handle_binary(self,
message: bytes)` on the connection class. They are not RPC envelopes.

## Authorization, state and broadcast

Override `authorize()` to inspect the connection's headers/cookies before
acceptance. In the bare adapter, `self.request` is an `ASGIWebSocket`; in a
FastAPI/Starlette endpoint it is that framework's WebSocket. The original
ASGI scope is always available as `self.scope`; application-provided connection
context is `self.context`. Returning `False` rejects the handshake with 403.

`RPC.as_asgi()` returns an isolated application with a snapshot of routes and
signals. Access its clients through `rpc.get_clients()` and use
`await rpc.broadcast("method", **params)` to gather client results. For direct
`RPC.serve()` integrations use `RPC.get_clients()` / `RPC.broadcast()` and a
separate handler subclass per application. Registries are local to the worker.

Register routes on the handler before `as_asgi()`. To modify a created
endpoint's registrations, use its `rpc.handler.add_route()` / `remove_route()`.
