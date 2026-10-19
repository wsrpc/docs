"""Runtime checks of the complete FastAPI browser and callback demos."""

import asyncio
import runpy
from pathlib import Path
from uuid import UUID

import pytest

pytest.importorskip("wsrpc_asgi")
httpx = pytest.importorskip("httpx")
fastapi = pytest.importorskip("fastapi")

from wsrpc_asgi import ClientException, WSRPCClient  # noqa: E402

from .test_frameworks import serve_app  # noqa: E402

EXAMPLES = Path(__file__).resolve().parents[1] / "asgi/examples"


def test_fastapi_browser_demo(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    server = runpy.run_path(str(EXAMPLES / "main/server.py"))
    client = runpy.run_path(str(EXAMPLES / "main/client.py"))

    async def scenario():
        async with serve_app(server["create_app"]()) as url:
            async with httpx.AsyncClient(
                base_url=url.replace("ws:", "http:")
            ) as http:
                page = await http.get("/web-client.html")
                assert page.status_code == 200
                assert "uuid4" in page.text
                script = await http.get("/js/wsrpc.min.js")
                assert script.status_code == 200
                assert len(script.content) > 1000
            await client["main"](url + "/ws/")

    asyncio.run(scenario())
    assert UUID(capsys.readouterr().out.strip()).version == 4


def test_fastapi_callback_demo():
    server = runpy.run_path(str(EXAMPLES / "server.py"))
    example_client = runpy.run_path(str(EXAMPLES / "client.py"))
    app = fastapi.FastAPI()

    @app.websocket("/ws/")
    async def endpoint(websocket: fastapi.WebSocket):
        await server["WebSocket"].serve(websocket)

    async def scenario():
        async with serve_app(app) as url:
            async with WSRPCClient(url + "/ws/") as client:
                client.add_route("joke", example_client["joke"])
                assert await client.proxy.test(message="Hello") == {
                    "message": "Hello"
                }
                assert await client.proxy.test.getJoke() == "Cool"
                with pytest.raises(ClientException):
                    await client.proxy.test._secure_method()

    asyncio.run(scenario())
