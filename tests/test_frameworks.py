"""Optional runtime checks of the imported ASGI documentation examples."""

import asyncio
import importlib
import socket
from contextlib import asynccontextmanager

import pytest

pytest.importorskip(
    "wsrpc_asgi", reason="Install the ASGI library for runtime checks"
)
httpx = pytest.importorskip("httpx")
uvicorn = pytest.importorskip("uvicorn")

from wsrpc_asgi import WSRPCClient  # noqa: E402


@asynccontextmanager
async def serve_app(app):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            log_level="error",
            lifespan="auto",
            ws="websockets-sansio",
        )
    )
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        for _ in range(500):
            if server.started:
                break
            if task.done():
                await task
                raise RuntimeError("Server failed to start")
            await asyncio.sleep(0.01)
        else:
            raise TimeoutError("Server startup timed out")
        yield f"ws://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(task, 10)
        finally:
            listener.close()


@pytest.mark.parametrize(
    "name,dependency",
    [
        ("bare", None),
        ("fastapi", "fastapi"),
        ("starlette", "starlette"),
        ("django", "django"),
        ("channels", "channels"),
        ("quart", "quart"),
        ("litestar", "litestar"),
        ("falcon", "falcon"),
        ("sanic", "sanic"),
        ("blacksheep", "blacksheep"),
    ],
)
def test_framework_example(name, dependency):
    if dependency:
        pytest.importorskip(dependency)

    async def scenario():
        module = importlib.import_module(f"asgi.examples.frameworks.{name}_app")
        async with serve_app(module.app) as url:
            async with WSRPCClient(url + "/ws/", timeout=3) as client:
                client.add_route("double", lambda socket, value: value * 2)
                assert await client.proxy.echo(message="Hello") == {
                    "message": "Hello"
                }
                assert await client.proxy.callback(value=21) == 42
            async with httpx.AsyncClient(
                base_url=url.replace("ws:", "http:")
            ) as http:
                response = await http.get("/health")
                if name == "bare":
                    assert response.status_code == 404
                else:
                    assert response.status_code == 200
                    assert response.json() == {"ok": True}

    asyncio.run(scenario())
