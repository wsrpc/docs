import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


class Scripts(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.active = False
        self.kind = "commonjs"
        self.scripts = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.active = True
            self.kind = (
                "module" if dict(attrs).get("type") == "module" else "commonjs"
            )

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False

    def handle_data(self, data):
        if self.active and data.strip():
            self.scripts.append((self.kind, data))


SOURCES = [
    *ROOT.glob("*.md"),
    *ROOT.glob("aiohttp/**/*.md"),
    *ROOT.glob("asgi/**/*.md"),
    *ROOT.glob("typescript/**/*.md"),
    *ROOT.glob("javascript/**/*.md"),
    *ROOT.glob("python/**/*.md"),
    *ROOT.glob("aiohttp/examples/**/*.html"),
    *ROOT.glob("asgi/examples/**/*.html"),
]


@pytest.mark.parametrize(
    "path", SOURCES, ids=lambda p: str(p.relative_to(ROOT))
)
def test_javascript_syntax(path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for JavaScript syntax checks")
    text = path.read_text()
    if path.suffix == ".html":
        scripts = Scripts(text).scripts
    else:
        scripts = [
            ("module", source)
            for source in re.findall(
                r"```javascript[^\n]*\n(.*?)\n```", text, re.S
            )
        ]
        for html in re.findall(r"```html[^\n]*\n(.*?)\n```", text, re.S):
            scripts += Scripts(html).scripts
    for kind, script in scripts:
        result = subprocess.run(
            [node, f"--input-type={kind}", "--check"],
            input=script,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, f"{path}: {result.stderr}"


@pytest.mark.parametrize(
    "path",
    [
        *ROOT.glob("typescript/examples/*.ts"),
        *ROOT.glob("typescript/**/*.md"),
        *ROOT.glob("javascript/**/*.md"),
    ],
    ids=lambda p: str(p.relative_to(ROOT)),
)
def test_typescript_syntax(path, tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node 24+ is required for TypeScript syntax checks")
    version = subprocess.check_output([node, "--version"], text=True)
    if int(version.lstrip("v").split(".")[0]) < 24:
        pytest.skip("Node 24+ is required for native TypeScript syntax checks")
    if path.suffix == ".ts":
        scripts = [path.read_text()]
    else:
        scripts = re.findall(
            r"```typescript[^\n]*\n(.*?)\n```", path.read_text(), re.S
        )
    for script in scripts:
        snippet = tmp_path / "snippet.mts"
        snippet.write_text(script)
        result = subprocess.run(
            [node, "--check", str(snippet)],
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, f"{path}: {result.stderr}"
