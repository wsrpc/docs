# Choosing a transport and migrating

The packages share the wire protocol, route concepts and RPC API. Their
WebSocket integration and lifecycle behavior differ.

| Concern | aiohttp | ASGI | TypeScript | Go |
| --- | --- | --- | --- | --- |
| Import | `wsrpc_aiohttp` | `wsrpc_asgi` | `@wsrpc/server` | `github.com/wsrpc/wsrpc-go` and `/ws` |
| Server integration | aiohttp handler class | ASGI callable or framework socket | HTTP upgrade or accepted `ws` socket | net/http handler or accepted socket |
| Parameters | Python keyword arguments | Python keyword arguments | One params object; arrays stay arrays | Tagged structs, maps or typed arrays |
| Metadata | aiohttp `Request` | ASGI scope or framework socket | `authorize(request)` result in `socket.context` | Explicit `context.Context` |
| Client transport | aiohttp | optional `websockets` | `ws` | `coder/websocket` |
| Timeout units | seconds | seconds | milliseconds | `context` deadlines / `time.Duration` |
| Binary input | `aiohttp.WSMessage` | `bytes` | `Uint8Array` | `[]byte` |
| Handler concurrency | asyncio tasks / threads | asyncio tasks / threads | Node event loop | Go goroutines |
| Broadcast | process-local | process-local | process-local | process-local |


For existing aiohttp applications, start with the [aiohttp guide](aiohttp/index.md).
For FastAPI, Starlette and other asyncio ASGI applications, use the
[ASGI framework guide](asgi/frameworks.md).

Migrating a server changes its transport integration and imports. Existing
clients can continue to use the same protocol. See the detailed
[ASGI migration guide](asgi/migration.md) for constructor, exception, cleanup
and concurrency differences. Trio backends are not supported by `wsrpc-asgi`.

The documentation is published as one site, with shared protocol and client
guides and separate transport-specific quick starts, API references and examples.

For Node HTTP, Express and Fastify, use the [TypeScript guide](typescript/index.md).
Its core shares the wire protocol, while JavaScript methods receive a params
object rather than Python keyword arguments. TypeScript has no automatic
threaded handler equivalent. Factory-created route objects remain per connection,
while ready objects may share application state. Their
`init` method is called only when the bare route name is explicitly invoked.

The [Go guide](go/index.md) uses explicit contexts and typed method handles.
Ready objects and per-connection factories are supported. Go code must synchronize
shared mutable state; it has no implicit goroutine-local RPC context or dynamic
property proxy. Existing browser applications still speak the same protocol.
