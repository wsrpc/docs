# WSRPC documentation

One documentation site for `wsrpc-aiohttp` and `wsrpc-asgi`, built with
Sphinx, MyST and Furo. Shared protocol/client guides and separate server
integration guides keep the transport-specific APIs explicit.

```shell
uv sync --locked
uv run --locked pytask
```

Open `_build/html/index.html` after building. The GitHub Actions workflow
checks pull requests and deploys successful builds from `main` to GitHub Pages.
The documentation domain is https://docs.wsrpc.org/.

The repository was extracted from `wsrpc-aiohttp` with `git filter-repo
--path docs/`, retaining only documentation history. Pages and configuration
live at the repository root. Library implementation code is not included.

Licensed under Apache-2.0; original attribution is retained.

See [maintaining the site](contributing.md) for API snapshots, optional ASGI
example checks, source provenance and GitHub Pages setup. Runtime examples
live under `aiohttp/examples/` and `asgi/examples/`.
