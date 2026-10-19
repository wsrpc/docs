import falcon.asgi
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


class Health:
    async def on_get(self, request, response):
        response.media = {"ok": True}


http_app = falcon.asgi.App()
http_app.add_route("/health", Health())
rpc = create_handler().as_asgi()
app = RPCMiddleware(http_app, rpc, path="/ws/")
