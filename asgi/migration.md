# Migrating from wsrpc-aiohttp

This project started as a fork of wsrpc-aiohttp. The new package is `wsrpc-asgi`
and the import namespace is `wsrpc_asgi`. The RPC envelopes and JavaScript
assets are compatible with wsrpc-aiohttp. Existing clients can connect to the
ASGI server; the new Python client can connect to an aiohttp server.

## Server changes

Replace aiohttp route registration with an ASGI integration from the
[framework guide](frameworks.md). `WebSocketAsync` and `WebSocketThreaded`
are connection classes, not aiohttp `AbstractView` implementations.

- Use `RPC.as_asgi()` for a standalone endpoint or an ASGI route.
- Use `await RPC.serve(websocket)` inside a FastAPI/Starlette endpoint.
- Use `RPCMiddleware` to compose an existing ASGI application.
- Move aiohttp-specific request inspection to `self.scope`, or the supplied
  framework WebSocket's `headers`, `cookies` and other properties.
- Override `handle_binary(message: bytes)` rather than handling an
  `aiohttp.WSMessage`.
- Replace aiohttp static routes with your framework's static file support.

Route methods, explicit `init`, decorators, `call`, `proxy`, `emit`, serializer
registration and signal argument names retain their existing shape.
Application snapshots and subclass-specific signals isolate state. Configure
and register routes/signals before calling `as_asgi()`.

Incoming calls now have an enforced execution limit and bounded pending
capacity. Cleanup is awaited, pending calls fail on disconnect, and handler
execution timeouts are enforced. These lifecycle fixes are intentional;
applications should not depend on leaked tasks or calls waiting indefinitely
after a disconnect.

## Python client changes

Install `wsrpc-asgi[client]`. `WSRPCClient` uses `websockets` rather than an
aiohttp `ClientSession`; the `session=` argument is not supported. Use an
absolute `ws://` or `wss://` endpoint. Transport options are arguments to
`websockets.asyncio.client.connect`, including `additional_headers`.

Handshake failures raise `websockets.exceptions.InvalidStatus`; use
`exc.response.status_code`. Transport closures can raise a websockets
`ConnectionClosed` exception; pending RPC calls fail with `ConnectionError`.
Client construction, `async with`, routes, calls and events otherwise retain
the same RPC interface.

The server package has no aiohttp dependency. aiohttp and wsrpc-aiohttp are
installed only in development to verify interoperability in both directions.
