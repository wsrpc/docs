# Python clients

The server transport and client transport can be chosen independently. Both
Python clients support reverse calls, events, route classes and `proxy`.

| Python client | Install | Transport |
| --- | --- | --- |
| `wsrpc_aiohttp.WSRPCClient` | `wsrpc-aiohttp` | aiohttp `ClientSession` |
| `wsrpc_asgi.WSRPCClient` | `wsrpc-asgi[client]` | `websockets.asyncio` |


The ASGI package's client connects with an absolute WebSocket URL:

```python
import asyncio
from wsrpc_asgi import WSRPCClient


async def main():
    async with WSRPCClient("ws://127.0.0.1:8000/ws/", timeout=5) as client:
        client.add_route("double", lambda socket, value: value * 2)
        print(await client.proxy.echo(message="Hello"))


if __name__ == "__main__":
    asyncio.run(main())
```

For the aiohttp client, import `WSRPCClient` from `wsrpc_aiohttp` instead;
the same call and callback syntax applies. Transport constructor options differ:
the aiohttp client supports a `session`, while the ASGI client's extra keywords
go to `websockets.asyncio.client.connect`.

Create a client inside an async function and close it using `async with`.
The aiohttp client closes its HTTP session, including a supplied session.
Do not share that session with resources that need to outlive the RPC client.

For complete runnable client/server pairs see the
[shared quick start](quick-start.md).

