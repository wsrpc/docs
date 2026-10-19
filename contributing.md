# Maintaining the documentation

## Build and check

The repository contains documentation, examples and site tooling. It has no
library implementation. From this checkout:

```shell
uv sync --locked
uv run --locked pytask
```

The tasks lint Python tooling and example files, execute named aiohttp Markdown
examples, compile Python snippets and build Sphinx with warnings treated as
errors. The final check follows every local HTML link, resource and fragment,
and verifies canonical URLs. Open `_build/html/index.html` to preview the site.

Documentation and development dependencies use the single `dev` group. The
locked environment installs the published aiohttp package for executable
examples; the site itself uses checked-in API reference snapshots and does
not import either library during Sphinx rendering.

## Update API references

Refresh signatures and docstrings from the corresponding library checkout:

```shell
uv run python tools/export_api.py ../wsrpc-aiohttp aiohttp
uv run python tools/export_api.py ../wsrpc-asgi asgi
```

The export reads Python syntax trees without importing or copying implementation
bodies. Review the changed reference, then run the complete checks. Public API
names retain their package-qualified anchors.

## Check ASGI integrations locally

The normal CI build checks ASGI Python syntax and the rendered API reference
without needing a private library checkout. Runtime framework tests are
optional and require installing the ASGI library explicitly:

```shell
uv sync --locked --group integrations
uv pip install --python .venv/bin/python -e ../wsrpc-asgi
uv run --no-sync --group integrations pytest tests/test_frameworks.py tests/test_asgi_runtime.py -q
```

These tests copy each standalone framework file to an empty temporary
directory, load it without the documentation package, and run it through
Uvicorn. They call RPC methods in both directions and check each framework's
HTTP health route. The aiohttp example is checked the same way using its
own HTTP server.
They also run the complete FastAPI browser and callback demos.
A normal `uv sync --locked` restores the standalone site environment.

## Source history and attribution

The initial history was extracted from `wsrpc-aiohttp` with
`git filter-repo --path docs/`. Only commits touching documentation survive.
The pages were then moved to the top level and the ASGI documentation was
imported into its own section. See `sources.toml` for the library source
revisions used during this extraction. Library implementation code is not
vendored in this repository. Keep copyright and license notices when updating
examples or assets.

The earlier quick-start URL redirects to the shared quick start. Other
root-level URLs from the earlier aiohttp site redirect to the corresponding
`aiohttp/` pages. The old API URL redirects directly to the API reference so
package-qualified class and method fragments remain available.

## GitHub Pages

The `pages.yml` workflow validates pull requests and builds pushes to `main`.
Only successful builds from `main`, including a manual dispatch on `main`, can
deploy. Pull requests have read-only permissions and never deploy. The deploy
job uses the `github-pages` environment, `pages: write` and `id-token: write`.

In the repository settings, select **Pages → Source → GitHub Actions**, set
**Custom domain** to `docs.wsrpc.org`, and configure DNS for that domain.
The source configuration sets canonical URLs to `https://docs.wsrpc.org/`.
Actions deployments do not use a checked-in CNAME file; the custom domain is
configured in Pages settings.

See [GitHub's custom-workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
for repository and environment requirements. GitHub Pages availability for a
private repository depends on the account's plan.
