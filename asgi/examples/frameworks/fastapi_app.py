from fastapi import Depends, FastAPI, WebSocket
from wsrpc_asgi import WebSocketAsync


class RPC(WebSocketAsync):
    pass


async def echo(socket, **params):
    return params


async def callback(socket, *, value):
    return await socket.proxy.double(value=value)


RPC.add_route("echo", echo)
RPC.add_route("callback", callback)


app = FastAPI()


async def connection_context(websocket: WebSocket):
    return {"client": websocket.client.host if websocket.client else None}


@app.websocket("/ws/")
async def rpc(websocket: WebSocket, context=Depends(connection_context)):
    await RPC.serve(websocket, context=context)


@app.get("/health")
async def health():
    return {"ok": True}
