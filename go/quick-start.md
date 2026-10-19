# Go quick start

Create an application with Go 1.27+:

```sh
mkdir myapp
cd myapp
go mod init example.com/myapp
go get github.com/wsrpc/wsrpc-go@main
```

Save this complete server as `main.go`. It registers a ready service object and
a `callback` method that calls `double` on the client.

```{literalinclude} examples/server/main.go
:language: go
```

```sh
go run .
```

The WebSocket endpoint is `ws://127.0.0.1:8000/ws/`. Try the
[Go client](client.md), [browser client](../javascript/client.md#browser),
or [Python client](../python/clients.md). The same methods are available to all
clients; only the host-language API changes.

The server implements `http.Handler`, so it can be mounted on routers that use
net/http. Authentication belongs in HTTP middleware or `ServerOptions.Authorize`.
For a long-running service, configure the enclosing HTTP server's timeouts and
use the [shutdown sequence](lifecycle.md).
