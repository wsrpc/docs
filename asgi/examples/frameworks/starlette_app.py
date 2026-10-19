from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from wsrpc_asgi import WebSocketAsync


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


rpc = create_handler().as_asgi()


@asynccontextmanager
async def lifespan(app):
    yield
    await rpc.close()


async def health(request):
    return JSONResponse({"ok": True})


app = Starlette(
    routes=[Route("/health", health), WebSocketRoute("/ws/", rpc)],
    lifespan=lifespan,
)
