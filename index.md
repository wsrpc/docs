# WSRPC

Bidirectional remote procedure calls over WebSockets. Both peers can expose
methods and receive results, errors and events over one connection.

```{card} Python
:link: python/index
:link-type: doc

Servers for aiohttp and ASGI frameworks, Python clients, routes and API reference.
```

```{card} JavaScript / TypeScript
:link: javascript/index
:link-type: doc

Node HTTP, Express and Fastify servers, browser and Node clients, typed contracts.
```

```{card} Go
:link: go/index
:link-type: doc

Typed server and client, net/http integration, ready route objects and context.
```

Choose a [quick start](quick-start.md) to run a complete example.
Python, JavaScript and Go implementations use the same protocol and can call each
other. Framework-specific setup belongs to the language guides.

```{toctree}
:hidden:
:maxdepth: 2
:caption: Languages

python/index
javascript/index
go/index
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: Shared reference

quick-start
protocol
compatibility
clients
contributing
```

Python, Go and the Node.js server are licensed under Apache-2.0; the JavaScript
client is licensed under MIT. Maintained by Dmitry Orlov
([orlovdl@gmail.com](mailto:orlovdl@gmail.com)).
