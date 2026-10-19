from wsrpc_aiohttp import WebSocketAsync

from aiohttp import web


class RPC(WebSocketAsync):
    pass


async def echo(socket, **params):
    return params


async def callback(socket, *, value):
    return await socket.proxy.double(value=value)


RPC.add_route("echo", echo)
RPC.add_route("callback", callback)


async def health(request):
    return web.json_response({"ok": True})


def create_app():
    app = web.Application()
    app.router.add_get("/ws/", RPC)
    app.router.add_get("/health", health)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="127.0.0.1", port=8000)
