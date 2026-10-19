# WSRPC

Bidirectional remote procedure calls over WebSockets. A Python or JavaScript
peer can expose methods, call the other peer and receive results, errors or
events over one connection.

Choose the server transport that fits your application:

| Your application | Package | Start here |
| --- | --- | --- |
| aiohttp | `wsrpc-aiohttp` | [aiohttp quick start](aiohttp/00-quick-start.md) |
| FastAPI, Starlette or another asyncio ASGI framework | `wsrpc-asgi` | [ASGI quick start](asgi/00-quick-start.md) |
| Django/Channels, Quart, Litestar, Falcon, Sanic or BlackSheep | `wsrpc-asgi` | [Framework integrations](asgi/frameworks.md) |
| Standalone asyncio ASGI endpoint | `wsrpc-asgi` | [Bare ASGI](asgi/frameworks.md#bare-asgi-and-other-frameworks) |

Both implementations use the same [WSRPC protocol](protocol.md). Existing
Python and JavaScript clients can connect across the two server transports.
The [client guide](clients.md) shows those choices; the
[compatibility guide](compatibility.md) explains the Python API differences.

```{toctree}
:maxdepth: 2
:caption: Shared concepts

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
