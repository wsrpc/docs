# Choosing a transport and migrating

The packages share the wire protocol, route concepts and RPC API. Their
WebSocket integration and lifecycle behavior differ.

| Concern | aiohttp | ASGI |
| --- | --- | --- |
| Python namespace | `wsrpc_aiohttp` | `wsrpc_asgi` |
| Server integration | aiohttp route with handler class | `as_asgi()`, `serve()` or `RPCMiddleware` |
| Connection metadata | aiohttp `Request` | ASGI scope or supplied framework WebSocket |
| Python client transport | aiohttp | optional `websockets` |
| Binary hook input | `aiohttp.WSMessage` | `bytes` |
| Async handler | `WebSocketAsync` | `WebSocketAsync` |
| Threaded handler | synchronous functions | synchronous functions; coroutine handlers awaited normally |
| Broadcast | worker-local | worker-local; isolated application registries available |

For existing aiohttp applications, start with the [aiohttp guide](aiohttp/index.md).
For FastAPI, Starlette and other asyncio ASGI applications, use the
[ASGI framework guide](asgi/frameworks.md).

Migrating a server changes its transport integration and imports. Existing
clients can continue to use the same protocol. See the detailed
[ASGI migration guide](asgi/migration.md) for constructor, exception, cleanup
and concurrency differences. Trio backends are not supported by `wsrpc-asgi`.

The documentation is published as one site, with shared protocol and client
guides and separate transport-specific quick starts, API references and examples.
