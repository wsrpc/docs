from litestar import Litestar, get
from wsrpc_asgi import RPCMiddleware, WebSocketAsync


def create_handler():
    class RPC(WebSocketAsync):
        pass

    async def echo(socket, **params):
        return params

    async def callback(socket, *, value):
        return await socket.proxy.double(value=value)

    RPC.add_route("echo", echo)
    RPC.add_route("callback", callback)
    return RPC


@get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


http_app = Litestar(route_handlers=[health])
rpc = create_handler().as_asgi()
app = RPCMiddleware(http_app, rpc, path="/ws/")
