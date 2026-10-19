# Go client

Create another application, add `github.com/wsrpc/wsrpc-go@main`, and save the
following as `main.go`. Run it while the Go quick-start server is running.

```{literalinclude} examples/client/main.go
:language: go
```

`Peer.Call[R]` decodes a result into `R`. To check both arguments and result at
compile time, use `peer.Method[Params, Result]("method").Call(ctx, params)`.
`peer.Remote("counter").Call[int](ctx, "add", params)` provides a namespace for
dotted calls. The method string still identifies a runtime protocol method;
independent servers can return incompatible data, reported as a decoding error.

The dial context covers the handshake. Every call has its own context and can
be cancelled without closing the connection. A local timeout stops local
waiting, and does not cancel remote application work: the shared protocol has no
cancellation message. Close and wait for the peer when the application is done.

Go's server/client roles are symmetric. A Go client can register callback
methods, receive events or binary data, and use the same typed signals as a server
peer. Python and TypeScript clients can call Go routes without a protocol adapter.
