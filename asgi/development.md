# Developing the ASGI library

Commands on this page apply to the **wsrpc-asgi library checkout**.
For this documentation repository, see [maintaining the site](../contributing.md).

The repository uses uv, pytask, Ruff, mypy, pytest, MyST, Sphinx and Furo.
Documentation and ordinary development dependencies share the `dev` group.
It includes the smaller `core-tests` group used by free-threaded CI.
The `integrations` group adds optional frameworks for the full example suite;
`serializers` adds a native codec solely for custom-codec testing.

```shell
uv sync --locked
uv run --locked pytask
```

Individual tasks can be selected with `-k`: `lint`, `typing`, `tests`,
`test_docs`, `docs`, `build`.

```shell
uv run --locked --group integrations pytest tests/test_examples.py
uv run --locked --group serializers pytest tests
```

## Verification

Tests use real WebSocket connections to Uvicorn; the suite also covers
Hypercorn, old/new Python peer interoperability and the unchanged bundled
JavaScript client. The JavaScript test needs Node 22+ with its browser-style
WebSocket API. Example tests run the actual files included in the documentation
and check both RPC callbacks and ordinary HTTP routes for each framework.

CI checks Python 3.10–3.15 and free-threaded 3.13–3.15, with Windows/macOS
smoke jobs. Optional framework integrations run separately on ordinary CPython;
some have native extensions whose free-threaded support is independent of this
library. Current Pydantic/PyO3 dependencies no longer build for Python 3.13t,
so free-threaded CI installs `core-tests` without the full development group:

```shell
uv sync --locked --no-default-groups --group core-tests
WSRPC_EXPECT_FREE_THREADED=1 uv run --locked --no-default-groups --group core-tests pytest tests --ignore=tests/test_examples.py
```

This still checks the bare ASGI server, Python clients in both directions,
Uvicorn, Hypercorn, reverse calls, errors, concurrency and cleanup. The core and default JSON codec do not need native extensions.

Set `WSRPC_EXPECT_FREE_THREADED=1` when testing a free-threaded interpreter.
The session fixture verifies that the GIL is disabled before and after tests.
Custom native codecs are tested only on regular CPython. Keep worker-local
asyncio objects on their owning event loop, including when using
`WebSocketThreaded`; threads receive handler execution, not ownership of the
connection transport.

## Documentation

The shared documentation site lives in [wsrpc/docs](https://github.com/wsrpc/docs).
See [maintaining the site](../contributing.md) for its build, example checks
and checked-in API references. The source examples shown in the ASGI guide
are included in that documentation repository.

## Packaging and release

`uv build` produces a wheel and sdist. The wheel includes `py.typed` and the
JavaScript assets. The sdist also contains documentation, examples and tests.
The upstream Apache-2.0 license and bundled JavaScript MIT license are retained.

The inherited publish workflow takes the version from a published GitHub
Release tag, runs `uv version`, builds distributions and publishes through
PyPI Trusted Publishing. Before using it for this fork, configure its own
repository, PyPI project and `pypi` environment. No public repository or
publisher is created by the local fork operation.
