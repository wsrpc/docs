# Go routes and context

## Ready objects and connection-owned state

`Router.Handle("name", service.Method)` registers a bound method on an initialized
object. Its dependencies and application state are kept. Only registered methods
are remotely accessible; exported methods are not automatically exposed.

Use `Options.Factory` to construct state for one connection:

```go
options := wsrpc.Options{
    Factory: func(peer *wsrpc.Peer, routes *wsrpc.Router) (func(), error) {
        counter := &Counter{DB: database}
        if err := routes.Handle("counter.add", counter.Add); err != nil {
            return nil, err
        }
        return counter.Close, nil
    },
}
```

Here `Counter.Add` has signature `func(context.Context, Params) (Result, error)`
and `Counter.Close` has signature `func()`. The factory runs once per connection,
before remote calls. Cleanup runs once after active handlers finish. Shared
mutable data must use mutexes or atomics: calls execute concurrently in Go.

`Router.Mount("counter", methods)` adds an explicitly registered method set under
a prefix. An `init` method additionally accepts the bare route name `counter`.
Constructing the object does not invoke `init`. Connection factories are eager;
use `sync.Once` inside a connection-owned object if construction should be lazy.

`Peer.Handle` adds or replaces a live connection's route, and `DeleteRoute` removes
it. Router registrations are snapshotted for each new connection.

## Context and reverse calls

Every handler receives `context.Context`. `wsrpc.FromContext(ctx)` gives the peer;
`wsrpc.Current(ctx)` gives its call ID and method as well. Pass the context into
helpers and new goroutines. Go does not have ambient `contextvars` or
`AsyncLocalStorage`, and a shared service must not swap its socket field for each
call.

The peer can call the other endpoint while the current handler runs:

```go
peer, ok := wsrpc.FromContext(ctx)
if !ok { return 0, errors.New("missing RPC context") }
return peer.Call[int](ctx, "double", params)
```

Use the handler's context to preserve call metadata. `peer.Context()` refers to
the connection lifetime and has no individual call metadata. Work that calls the
remote endpoint at connection startup belongs in `Server.OnConnect`; factory
setup has not started the reader yet.

JSON argument objects map to tagged Go structs rather than keyword arguments.
Missing fields get zero values and unknown fields are ignored; validate required
inputs in application code. JSON maps decode numbers as `json.Number`. Arbitrary
integers sent to ordinary JavaScript JSON consumers should be encoded as strings.
