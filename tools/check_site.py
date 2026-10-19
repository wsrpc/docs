"""Check local links, resources, fragments and canonical URLs."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE = "https://docs.wsrpc.org/"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.canonical = []
        self.refresh = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"])
        for attr in ("href", "src"):
            if data.get(attr):
                self.links.append(data[attr])
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical.append(data.get("href"))
        if tag == "meta" and data.get("http-equiv", "").lower() == "refresh":
            self.refresh.append(data.get("content", ""))


def check(root):
    root = root.resolve()
    pages = {path: Page(path) for path in root.rglob("*.html")}
    errors = []
    for path, page in pages.items():
        relative = path.relative_to(root).as_posix()
        if not page.refresh and page.canonical != [BASE + relative]:
            errors.append(f"{relative}: incorrect canonical {page.canonical}")
        for link in page.links:
            parts = urlsplit(link)
            if (
                parts.scheme
                or parts.netloc
                or not parts.path
                and not parts.fragment
            ):
                continue
            if not parts.path:
                target = path
            elif parts.path.startswith("/"):
                target = root / unquote(parts.path).lstrip("/")
            else:
                target = path.parent / unquote(parts.path)
            target = target.resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"{relative}: missing target {link}")
            elif (
                parts.fragment
                and target in pages
                and unquote(parts.fragment) not in pages[target].ids
            ):
                errors.append(f"{relative}: missing anchor {link}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(pages)} pages: links, assets, anchors and canonicals")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    check(parser.parse_args().root)
