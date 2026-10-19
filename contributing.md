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
```

The export reads Python syntax trees without importing or copying implementation
bodies. Review the changed reference, then run the complete checks. Public API
names retain their package-qualified anchors.

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
