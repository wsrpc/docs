from datetime import datetime

project = "WSRPC"
author = "Dmitry Orlov"
copyright = f"{datetime.now().year}, {author}"
extensions = ["myst_parser", "sphinx_reredirects", "sphinx_design"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
myst_heading_anchors = 3
html_theme = "furo"
html_static_path = ["_static"]
html_favicon = "_static/Icon.png"
html_baseurl = "https://docs.wsrpc.org/"
html_title = "WSRPC documentation"
html_theme_options = {
    "light_logo": "logo_light.svg",
    "dark_logo": "logo_dark.svg",
    "sidebar_hide_name": False,
    "source_repository": "https://github.com/wsrpc/docs/",
    "source_branch": "main",
    "source_directory": "",
}
redirects = {
    "00-quick-start": "quick-start.html",
    "01-introduction": "aiohttp/01-introduction.html",
    "02-signals": "aiohttp/02-signals.html",
    "apidoc": "aiohttp/api.html",
    "development": "aiohttp/development.html",
}
exclude_patterns = [
    ".git/**",
    ".pytest_cache/**",
    ".pytask/**",
    ".ruff_cache/**",
    "tools/**",
    "tests/**",
    "**/examples/**",
    "_build/**",
    ".venv/**",
    "README.md",
]
