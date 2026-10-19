# Quick start

Expose methods at `/ws/`, connect once, then call in either direction.
Choose your framework below. Installation and server tabs stay in sync;
the Python and browser clients work with every server shown here.

## Install

Use Python 3.10+ in a virtual environment. Install the package for your server:

`````{tab-set}
:sync-group: framework

````{tab-item} aiohttp
:sync: aiohttp

```shell
pip install wsrpc-aiohttp
```
````

````{tab-item} FastAPI
:sync: fastapi

```shell
pip install 'wsrpc-asgi[client,fastapi]' uvicorn
```
````

````{tab-item} Starlette
:sync: starlette

```shell
pip install 'wsrpc-asgi[client,starlette]' uvicorn
```
````

````{tab-item} Django
:sync: django

```shell
pip install 'wsrpc-asgi[client]' django uvicorn
```
````

````{tab-item} Channels
:sync: channels

```shell
pip install 'wsrpc-asgi[client]' django channels uvicorn
```
````

````{tab-item} Quart
:sync: quart

```shell
pip install 'wsrpc-asgi[client]' quart uvicorn
```
````

````{tab-item} Litestar
:sync: litestar

```shell
pip install 'wsrpc-asgi[client]' litestar uvicorn
```
````

````{tab-item} Falcon
:sync: falcon

```shell
pip install 'wsrpc-asgi[client]' falcon uvicorn
```
````

````{tab-item} Sanic
:sync: sanic

```shell
pip install 'wsrpc-asgi[client]' sanic uvicorn
```
````

````{tab-item} BlackSheep
:sync: blacksheep

```shell
pip install 'wsrpc-asgi[client]' blacksheep uvicorn
```
````

````{tab-item} Bare ASGI
:sync: bare

```shell
pip install 'wsrpc-asgi[client]' uvicorn
```
````

`````

## Define the RPC methods

Every server below exposes the same two methods: `echo` returns its keyword
arguments, and `callback` asks the client to double a value.

For **aiohttp**, the complete server below includes these methods.
Create a `myapp` directory with an empty `myapp/__init__.py`.
For **ASGI frameworks**, save this
shared route definition as `myapp/common.py`:

```{literalinclude} asgi/examples/frameworks/common.py
:language: python
```

## Connect your server

Save the selected server as `myapp/app.py`. ASGI examples import the shared
`common.py` above. Start the server with the command in the same tab.
All examples listen at `ws://127.0.0.1:8000/ws/`; all except bare ASGI also
serve `GET /health` as an ordinary HTTP route.

`````{tab-set}
:sync-group: framework

````{tab-item} aiohttp
:sync: aiohttp

```{literalinclude} aiohttp/examples/frameworks/app.py
:language: python
```

```shell
python -m myapp.app
```
````

````{tab-item} FastAPI
:sync: fastapi

`serve()` accepts an unaccepted FastAPI WebSocket. Dependencies run once per connection; their results are available through `socket.context`.

```{literalinclude} asgi/examples/frameworks/fastapi_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Starlette
:sync: starlette

Keep the endpoint and close it in the application's lifespan, as shown here.

```{literalinclude} asgi/examples/frameworks/starlette_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Django
:sync: django

This standalone example configures minimal settings. In an existing project keep your `DJANGO_SETTINGS_MODULE`. The RPC wrapper bypasses Django HTTP middleware; authorize WebSockets separately.

```{literalinclude} asgi/examples/frameworks/django_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Channels
:sync: channels

Also copy [django_app.py](asgi/examples/frameworks/django_app.py) to `myapp/django_app.py`; it supplies the HTTP application and standalone settings. In an existing Channels project retain its settings and authentication/origin middleware.

```{literalinclude} asgi/examples/frameworks/channels_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Quart
:sync: quart

```{literalinclude} asgi/examples/frameworks/quart_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Litestar
:sync: litestar

```{literalinclude} asgi/examples/frameworks/litestar_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Falcon
:sync: falcon

```{literalinclude} asgi/examples/frameworks/falcon_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Sanic
:sync: sanic

Run through Uvicorn in ASGI mode so the RPC wrapper receives connections.

```{literalinclude} asgi/examples/frameworks/sanic_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} BlackSheep
:sync: blacksheep

```{literalinclude} asgi/examples/frameworks/blacksheep_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

````{tab-item} Bare ASGI
:sync: bare

The endpoint itself is an ASGI callable. Use an asyncio server backend.

```{literalinclude} asgi/examples/frameworks/bare_app.py
:language: python
```

```shell
uvicorn myapp.app:app --host 127.0.0.1 --port 8000
```
````

`````

Each handler receives the current RPC connection as its first argument.
Expose only the methods you intend peers to call. See
[ASGI integration details](asgi/frameworks.md) for authentication, lifecycle,
server backends and deployment; [aiohttp routes](aiohttp/01-introduction.md)
cover aiohttp-specific handler behavior.

## Call from Python

Use either Python client with **any** server above. Save as `client.py`,
then run `python client.py` while the server is running. The callback is
registered before connecting, so the server can call it immediately.

`````{tab-set}
:sync-group: client

````{tab-item} aiohttp client
:sync: wsrpc_aiohttp

```python
import asyncio
from wsrpc_aiohttp import WSRPCClient


async def main():
    async with WSRPCClient("ws://127.0.0.1:8000/ws/", timeout=5) as client:
        client.add_route("double", lambda socket, value: value * 2)
        print(await client.proxy.echo(message="Hello"))
        print(await client.proxy.callback(value=21))


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output:

```text
{'message': 'Hello'}
42
```
````

````{tab-item} websockets client
:sync: wsrpc_asgi

```python
import asyncio
from wsrpc_asgi import WSRPCClient


async def main():
    async with WSRPCClient("ws://127.0.0.1:8000/ws/", timeout=5) as client:
        client.add_route("double", lambda socket, value: value * 2)
        print(await client.proxy.echo(message="Hello"))
        print(await client.proxy.callback(value=21))


if __name__ == "__main__":
    asyncio.run(main())
```

Expected output:

```text
{'message': 'Hello'}
42
```
````

`````

Install `wsrpc-aiohttp` for the aiohttp client, or `wsrpc-asgi[client]` for
the websockets client. Calls use keyword arguments. The context manager
connects on entry and closes the connection on exit. Use `wss://` with TLS.

## Call from a browser

Both packages include the same JavaScript client. Serve `STATIC_DIR` at
`/js/` using your framework's static-file support, then use the same code
with every server:

```html
<script src="/js/wsrpc.min.js"></script>
<script>
  const scheme = location.protocol === "https:" ? "wss:" : "ws:";
  const rpc = new WSRPC(`${scheme}//${location.host}/ws/`);
  rpc.addRoute("double", ({ value }) => value * 2);
  rpc.connect();

  async function run() {
    await rpc.onEvent("onconnect");
    try {
      console.log(await rpc.call("echo", { message: "Hello" }));
      console.log(await rpc.call("callback", { value: 21 }));
    } catch (error) {
      console.error(error);
    }
  }
  run();
</script>
```

For complete demos that serve both the page and JavaScript, see the
[aiohttp browser demo](aiohttp/00-quick-start.md) and
[FastAPI browser demo](asgi/00-quick-start.md). Continue with
[clients](clients.md), [the protocol](protocol.md) or
[API differences](compatibility.md).
