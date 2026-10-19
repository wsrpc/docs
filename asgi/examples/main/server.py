import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from wsrpc_asgi import STATIC_DIR, WebSocketAsync


class Socket(WebSocketAsync):
    pass


async def get_random_uuid(socket: Socket) -> str:
    return str(uuid.uuid4())


def create_app() -> FastAPI:
    Socket.add_route("uuid4", get_random_uuid)
    app = FastAPI()

    @app.websocket("/ws/")
    async def rpc(websocket: WebSocket):
        await Socket.serve(websocket)

    app.mount("/js", StaticFiles(directory=STATIC_DIR), name="js")
    app.mount("/", StaticFiles(directory=Path(__file__).parent, html=True))
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
