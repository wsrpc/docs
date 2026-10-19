# WSRPC

Bidirectional remote procedure calls over WebSockets. A Python or JavaScript
peer can expose methods, call the other peer and receive results, errors or
events over one connection.

[Get started](quick-start.md): install a package, choose your framework tab,
and run the same RPC call from Python or a browser. Examples cover aiohttp,
FastAPI, Starlette, Django, Channels, Quart, Litestar, Falcon, Sanic,
BlackSheep and bare ASGI.

Both implementations use the same [WSRPC protocol](protocol.md). Existing
Python and JavaScript clients can connect across the two server transports.
The [client guide](clients.md) shows those choices; the
[compatibility guide](compatibility.md) explains the Python API differences.

```{toctree}
:maxdepth: 2
:caption: Getting started

quick-start
protocol
clients
compatibility
```

```{toctree}
:maxdepth: 2
:caption: Server integrations

aiohttp/index
asgi/index
```

```{toctree}
:maxdepth: 1
:caption: Contributing

contributing
```

The Python projects are licensed under Apache-2.0; the bundled JavaScript
client retains its MIT license. Maintained by Dmitry Orlov
([orlovdl@gmail.com](mailto:orlovdl@gmail.com)).
