# Portable core and Workers

For a Worker, import `RPCPeer` from `@wsrpc/client/core` and connect it to the
host's WebSocket API. Use `@wsrpc/server` for Node.js applications instead.
Deno, Bun and native browser transports can use the same core interface.

## Cloudflare Worker

This example accepts a WebSocketPair and feeds messages to the core. The host
owns WebSocket upgrades, payload limits and authorization.

```{literalinclude} ../typescript/examples/worker.ts
:language: typescript
```

No `nodejs_compat` flag is required. `server.binaryType = "arraybuffer"` selects
synchronous byte access for binary messages. See
[Cloudflare's WebSocket API](https://developers.cloudflare.com/workers/runtime-apis/websockets/)
for lifecycle and host settings.

Use the explicit socket argument or connection-bound Route classes. Implicit
async-local context requires a host-provided context storage; the Node adapter
installs that automatically.

Deno/Bun consumers supply a native Transport using the same `send`, `close`
and `receive` interface; there is no separate adapter package for those hosts.
