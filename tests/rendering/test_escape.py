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
