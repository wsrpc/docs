"""Compile all Python examples; named aiohttp blocks also execute via pytest."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = [*ROOT.glob("*.md"), *ROOT.glob("aiohttp/**/*.md")]
PYTHON = [*ROOT.glob("aiohttp/examples/**/*.py")]


@pytest.mark.parametrize("path", PYTHON, ids=lambda p: str(p.relative_to(ROOT)))
def test_example_syntax(path):
    ast.parse(path.read_text(), filename=str(path))


@pytest.mark.parametrize(
    "path", MARKDOWN, ids=lambda p: str(p.relative_to(ROOT))
)
def test_markdown_python_syntax(path):
    for index, source in enumerate(
        re.findall(r"```python[^\n]*\n(.*?)\n```", path.read_text(), re.S)
    ):
        compile(
            source,
            f"{path}:{index}",
            "exec",
            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
