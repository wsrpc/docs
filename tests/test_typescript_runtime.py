"""Optional checks of standalone docs examples against a packed npm artifact."""

import asyncio
import json
import os
import shutil
import socket
import subprocess
from pathlib import Path

import pytest
from wsrpc_aiohttp import WSRPCClient

from aiohttp import ClientConnectorError, ClientSession

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def node_project(tmp_path_factory):
    artifacts = [
        os.environ.get("WSRPC_TS_CLIENT"),
        os.environ.get("WSRPC_TS_SERVER"),
    ]
    if not all(artifacts):
        pytest.skip(
            "Set WSRPC_TS_CLIENT and WSRPC_TS_SERVER to built npm archives"
        )
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        pytest.skip("Node 24+ and npm are required")
    version = subprocess.check_output([node, "--version"], text=True)
    if int(version.lstrip("v").split(".")[0]) < 24:
        pytest.skip("Node 24+ is required for native TypeScript examples")
    project = tmp_path_factory.mktemp("typescript-docs")
    (project / "package.json").write_text(
        json.dumps({"private": True, "type": "module"})
    )
    subprocess.run(
        [
            npm,
            "install",
            *(str(Path(artifact).resolve()) for artifact in artifacts),
            "express",
            "fastify",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
        ],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    for path in (ROOT / "typescript/examples").glob("*.ts"):
        shutil.copy(path, project / path.name)
    return node, project


@pytest.mark.parametrize("framework", ["http", "express", "fastify"])
def test_standalone_typescript_application(node_project, framework):
    node, project = node_project

    async def scenario():
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        process = await asyncio.create_subprocess_exec(
            node,
            f"{framework}.ts",
            cwd=project,
            env={**os.environ, "PORT": str(port)},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            async with ClientSession() as http:
                for _ in range(500):
                    try:
                        async with http.get(
                            f"http://127.0.0.1:{port}/health"
                        ) as response:
                            assert response.status == 200
                            assert await response.json() == {"ok": True}
                            break
                    except ClientConnectorError:
                        if process.returncode is not None:
                            raise AssertionError(
                                (await process.stderr.read()).decode()
                            )
                        await asyncio.sleep(0.01)
                else:
                    raise TimeoutError("Node example startup timed out")
            url = f"ws://127.0.0.1:{port}/ws/"
            async with WSRPCClient(url, timeout=3) as client:
                client.add_route("double", lambda socket, value: value * 2)
                assert await client.proxy.echo(message="Hello") == {
                    "message": "Hello"
                }
                assert await client.proxy.callback(value=21) == 42
            client = await asyncio.create_subprocess_exec(
                node,
                "client.ts",
                url,
                cwd=project,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                output, errors = await asyncio.wait_for(client.communicate(), 5)
                assert client.returncode == 0, errors.decode()
                assert b"42" in output
            finally:
                if client.returncode is None:
                    client.kill()
                    await client.wait()
        finally:
            if process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 5)
                except TimeoutError:
                    process.kill()
                    await process.wait()

    asyncio.run(scenario())
