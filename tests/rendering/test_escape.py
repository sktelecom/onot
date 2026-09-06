# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""HTML escaping regression (§8.1): user input never reaches output verbatim."""

from __future__ import annotations

from onot.core.config import CompanyConfig, Settings
from onot.domain.models import Copyright, License, LicenseExpression, NoticeDocument, Package
from onot.rendering import render


def test_html_escapes_copyright_script():
    doc = NoticeDocument(
        name="prod",
        packages=(Package(name="p", copyright=Copyright(text="<script>alert('x')</script>")),),
    )
    html = render(doc, "html")
    assert "&lt;script&gt;" in html
    assert "<script>alert" not in html


def test_html_escapes_product_and_license_text():
    doc = NoticeDocument(
        name="A & B <co>",
        licenses=(License(license_id="X", name="L<i>", text="a < b & c"),),
    )
    html = render(doc, "html")
    assert "A &amp; B &lt;co&gt;" in html
    assert "a &lt; b &amp; c" in html
    assert "<co>" not in html


def test_markdown_escapes_package_name_pipe_and_link():
    # O-8: untrusted package name/version must not break the table or inject an active link.
    doc = NoticeDocument(
        name="prod",
        packages=(
            Package(
                name="evil | X | [a](javascript:alert(1))",
                version="1",
                license_concluded=LicenseExpression(raw="MIT"),
            ),
        ),
    )
    md = render(doc, "markdown")
    row = next(line for line in md.splitlines() if "evil" in line)
    assert "\\|" in row  # pipe escaped -> cell not split
    assert "\\[a\\]" in row  # link syntax neutralized
    assert "MIT" in row  # all cells stayed on one row (table structure intact)


def test_markdown_escapes_company_field_link():
    # O-10: company config fields are untrusted in Markdown output too.
    doc = NoticeDocument(name="prod")
    settings = Settings(company=CompanyConfig(copyright_holder="[x](javascript:alert(1))"))
    md = render(doc, "markdown", settings=settings)
    line = next(line for line in md.splitlines() if "javascript" in line)
    assert "\\[x\\]" in line


def test_theme_css_is_not_html_escaped():
    """<style> is a raw-text element, so an escaped quote there stays literal.

    Autoescaping the stylesheet turned every quoted font name into &#34;...&#34;, which made
    the whole font-family declaration invalid and left notices in the default serif.
    """
    html = render(NoticeDocument(name="prod"), "html")
    style = html[html.index("<style>") : html.index("</style>")]
    assert '"Segoe UI"' in style
    assert "&#34;" not in style
    assert "&amp;" not in style


def test_document_content_is_still_escaped():
    """The stylesheet is trusted package data; nothing else in the notice is."""
    doc = NoticeDocument(name='prod<script>alert("x")</script>')
    html = render(doc, "html")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
