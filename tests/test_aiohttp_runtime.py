import asyncio
import runpy
from pathlib import Path
from uuid import UUID

from aiohttp.test_utils import TestServer

from aiohttp import ClientSession

ROOT = Path(__file__).resolve().parents[1]


def test_aiohttp_quick_start_files(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    server = runpy.run_path(str(ROOT / "aiohttp/examples/main/server.py"))
    client = runpy.run_path(str(ROOT / "aiohttp/examples/main/client.py"))

    async def scenario():
        async with TestServer(server["create_app"]()) as http:
            async with ClientSession() as session:
                async with session.get(
                    http.make_url("/web-client.html")
                ) as page:
                    assert page.status == 200
                    assert "uuid4" in await page.text()
                async with session.get(
                    http.make_url("/js/wsrpc.min.js")
                ) as script:
                    assert script.status == 200
                    assert len(await script.read()) > 1000
            await client["main"](str(http.make_url("/ws/")))

    asyncio.run(scenario())
    assert UUID(capsys.readouterr().out.strip()).version == 4
