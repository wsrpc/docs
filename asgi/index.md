# ASGI server

WSRPC provides two-way remote procedure calls over one WebSocket connection.
Both peers can expose methods, make concurrent calls and receive results or
remote exceptions. This project is an ASGI fork of
[wsrpc-aiohttp](https://github.com/wsrpc/wsrpc-aiohttp), preserving its RPC
protocol and bundled JavaScript clients.

The server uses the standard ASGI interface and has no runtime dependencies.
The optional Python client uses `websockets`. Python 3.10+ and asyncio are
supported, including free-threaded CPython. Trio event loops are not supported.

```shell
pip install 'wsrpc-asgi[fastapi,client]' uvicorn
```

Start with the [Python quick start](../python/quick-start.md) and choose your framework tab.
The pages below cover transport-specific behavior and complete browser demos.

```{toctree}
:maxdepth: 2

00-quick-start
frameworks
01-introduction
02-signals
migration
development
apidoc
```

For aiohttp applications, see the [aiohttp guide](../aiohttp/index.md).

Created by Dmitry Orlov. The Python library is licensed under Apache-2.0;
the bundled JavaScript client is licensed under MIT.
