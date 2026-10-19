# Go events and lifecycle

`peer.Emit(ctx, event)` sends an object without an `id`.
`peer.SendRaw(ctx, data, true)` sends a binary message. Incoming data is available
through `OnEvent` and `OnBinary` signals. A signal's `Connect` method returns an
unsubscribe function.

`OnCallStart`, `OnCallSuccess`, `OnCallFail`, `OnError` and `OnClose` expose the
call and connection lifecycle. Listener panics/errors are reported and isolated;
listeners must return or honor context cancellation. Errors from `OnError` itself
are terminal and do not recursively invoke error reporting.

Returned Go errors become `{type, message}`; `*wsrpc.Failure` sets an explicit
remote type. `*wsrpc.RemoteError` retains the original remote JSON payload,
including string errors returned by legacy JavaScript callbacks.

`server.Broadcast[R](ctx, method, params)` returns a separate value/error outcome
for every peer. It is process-local, as in the other implementations.

Shut down both WebSocket RPC and HTTP:

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := rpc.Shutdown(ctx); err != nil { return err }
return httpServer.Shutdown(ctx)
```

For an individual peer, call `Close` and then `Wait`. Closing releases pending
callers and cancels connection-scoped contexts; waiting joins cooperative handlers
and runs route cleanup once. Never call `Wait` inside that peer's handler or signal.

Defaults are 1 MiB incoming messages, 10-second writes, 1024 pending calls, 128
concurrent handlers/events, and 8 MiB queued/in-flight writes. The queue also has
a 128-message bound. Calls use their caller's deadline; set one in application
code. Configure limits with `ServerOptions` and `wsrpc.Options`.

Go `[]byte` encodes as base64 inside JSON. Use raw WebSocket binary for binary
payloads or convert to explicit JSON integer arrays when the peer expects arrays.
Custom JSON marshaler/unmarshaler types work with the standard Go codec. The
initial API does not add arbitrary alternate wire codecs or automatic reconnect.
