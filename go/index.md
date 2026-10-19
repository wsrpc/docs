# Go

`wsrpc-go` provides a typed server and client speaking the same protocol as the
Python and JavaScript implementations. Use it with Go **1.27+**.

The root `github.com/wsrpc/wsrpc-go` package contains the RPC core and routes.
The `github.com/wsrpc/wsrpc-go/ws` package supplies a net/http server and dialer
using `github.com/coder/websocket`. There is no WebSocket implementation in the
Go standard library.

```{toctree}
:maxdepth: 1

quick-start
client
routes
lifecycle
```

Source and API: [wsrpc/wsrpc-go](https://github.com/wsrpc/wsrpc-go).
