# Python and JavaScript clients

The server transport and client transport can be chosen independently. Both
Python clients support reverse calls, events, route classes and `proxy`.

| Python client | Install | Transport |
| --- | --- | --- |
| `wsrpc_aiohttp.WSRPCClient` | `wsrpc-aiohttp` | aiohttp `ClientSession` |
| `wsrpc_asgi.WSRPCClient` | `wsrpc-asgi[client]` | `websockets.asyncio` |

## Python

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

## Browser

Both Python distributions include the same JavaScript client and TypeScript
declarations in `STATIC_DIR`. Serve those files through your framework's
static-file support or obtain the client through `npm install @wsrpc/client`.

```html
<script src="/js/wsrpc.min.js"></script>
<script>
  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  const rpc = new WSRPC(`${scheme}//${window.location.host}/ws/`);
  rpc.addRoute("double", ({ value }) => value * 2);
  rpc.connect();

  async function echo() {
    await rpc.onEvent("onconnect");
    try {
      console.log(await rpc.call("echo", { message: "Hello" }));
    } catch (error) {
      console.error(error);
    }
  }

  echo();
</script>
```

When using the module build, import the default export from `wsrpc.es6.js`.
Existing JavaScript clients use the same protocol with either server.
