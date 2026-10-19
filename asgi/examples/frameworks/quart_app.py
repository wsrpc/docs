from quart import Quart
from wsrpc_asgi import RPCMiddleware, WebSocketAsync


class RPC(WebSocketAsync):
    pass


async def echo(socket, **params):
    return params


async def callback(socket, *, value):
    return await socket.proxy.double(value=value)


RPC.add_route("echo", echo)
RPC.add_route("callback", callback)


app = Quart(__name__)


@app.get("/health")
async def health():
    return {"ok": True}


rpc = RPC.as_asgi()
app.asgi_app = RPCMiddleware(app.asgi_app, rpc, path="/ws/")
