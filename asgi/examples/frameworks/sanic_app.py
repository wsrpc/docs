from sanic import Sanic
from sanic.response import json
from wsrpc_asgi import RPCMiddleware, WebSocketAsync


class RPC(WebSocketAsync):
    pass


async def echo(socket, **params):
    return params


async def callback(socket, *, value):
    return await socket.proxy.double(value=value)


RPC.add_route("echo", echo)
RPC.add_route("callback", callback)


http_app = Sanic("wsrpc_example")


@http_app.get("/health")
async def health(request):
    return json({"ok": True})


rpc = RPC.as_asgi()
app = RPCMiddleware(http_app, rpc, path="/ws/")
