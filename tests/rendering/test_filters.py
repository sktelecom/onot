"""Jinja 필터: anchor 슬러그, license_links 토큰 링크화 + 이스케이프."""

from __future__ import annotations

from onot.rendering.filters import anchor, license_links, md_code_block


def test_anchor():
    assert anchor("GPL-2.0-only") == "GPL-2.0-only"
    assert anchor("Foo Bar!") == "Foo_Bar"


def test_license_links_wraps_known_ids():
    out = str(license_links("MIT OR Apache-2.0", ["MIT", "Apache-2.0"]))
    assert '<a href="#MIT">MIT</a>' in out
    assert '<a href="#Apache-2.0">Apache-2.0</a>' in out


def test_license_links_longest_first_no_partial_clobber():
    out = str(license_links("MITNFA OR MIT", ["MIT", "MITNFA"]))
    assert '<a href="#MITNFA">MITNFA</a>' in out
    assert '<a href="#MIT">MIT</a>' in out


def test_license_links_escapes_unknown_tokens():
    out = str(license_links("<evil> AND MIT", ["MIT"]))
    assert "&lt;evil&gt;" in out
    assert "<evil>" not in out


def test_md_code_block_default_fence():
    assert md_code_block("plain text") == "```text\nplain text\n```"


def test_md_code_block_escapes_inner_fence():
    # 본문에 ``` 가 있으면 더 긴 펜스로 감싸 fence 탈출을 막는다
    out = md_code_block("before ``` after")
    assert out.startswith("````text\n")
    assert out.endswith("\n````")
