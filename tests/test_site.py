import pytest

from tools.check_site import check


def test_site_check_resolves_self_fragments_and_relative_assets(tmp_path):
    (tmp_path / "index.html").write_text("""
<link rel="canonical" href="https://docs.wsrpc.org/index.html">
<h1 id="home">Home</h1><a href="#home">Home</a>
<a href="child.html#value">Child</a><img src="image.svg">
""")
    (tmp_path / "child.html").write_text("""
<link rel="canonical" href="https://docs.wsrpc.org/child.html">
<h1 id="value">Value</h1><a href="index.html#home">Home</a>
""")
    (tmp_path / "image.svg").write_text("<svg/>")
    check(tmp_path)
    (tmp_path / "image.svg").unlink()
    with pytest.raises(SystemExit, match="missing target image.svg"):
        check(tmp_path)


def test_site_check_rejects_broken_fragments(tmp_path):
    (tmp_path / "index.html").write_text("""
<link rel="canonical" href="https://docs.wsrpc.org/index.html">
<a href="#absent">Missing</a>
""")
    with pytest.raises(SystemExit, match="missing anchor #absent"):
        check(tmp_path)
