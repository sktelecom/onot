# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""HTML 이스케이프 회귀(§8.1): 사용자 입력이 출력에 그대로 들어가지 않는다."""

from __future__ import annotations

from onot.domain.models import Copyright, License, NoticeDocument, Package
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
