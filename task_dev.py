"""Run the complete documentation checks with uv run pytask."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


def run(*args: str) -> None:
    subprocess.run([sys.executable, "-m", *args], cwd=ROOT, check=True)


def task_lint() -> None:
    run("ruff", "check", ".")
    run("ruff", "format", "--check", ".")


def task_test_docs() -> None:
    run("pytest", "tests", "aiohttp", "-q")


def task_build() -> None:
    shutil.rmtree(ROOT / "_build/html", ignore_errors=True)
    run("sphinx", "-E", "-W", "--keep-going", "-b", "html", ".", "_build/html")
    (ROOT / "_build/html/.nojekyll").touch()
    subprocess.run(
        [sys.executable, "tools/check_site.py", "_build/html"],
        cwd=ROOT,
        check=True,
    )
