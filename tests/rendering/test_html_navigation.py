# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Navigation inside an HTML notice: contents, licence anchors, links back to the components."""

from __future__ import annotations

import re

from onot.domain.models import License, LicenseExpression, NoticeDocument, Package, PackageRef
from onot.rendering import render


def _doc(license_count: int = 2) -> NoticeDocument:
    ids = [f"LIC-{index}" for index in range(license_count)]
    packages = tuple(
        Package(name=f"pkg{index}", version="1", license_concluded=LicenseExpression(raw=lic))
        for index, lic in enumerate(ids)
    )
    licenses = tuple(
        License(
            license_id=lic,
            name=f"License {index}",
            text="body",
            used_by=(PackageRef(name=f"pkg{index}", version="1"),),
        )
        for index, lic in enumerate(ids)
    )
    return NoticeDocument(name="prod", packages=packages, licenses=licenses)


def _hrefs(html: str) -> set[str]:
    return {match[1:] for match in re.findall(r'href="(#[^"]+)"', html)}


def _ids(html: str) -> set[str]:
    return set(re.findall(r'id="([^"]+)"', html))


def test_every_internal_link_has_a_target():
    """A dangling anchor is a dead end for the reader and invisible in review."""
    html = render(_doc(3), "html")
    assert _hrefs(html) <= _ids(html)


def test_contents_lists_the_sections_and_every_licence():
    html = render(_doc(3), "html")
    contents = html[html.index("<nav") : html.index("</nav>")]
    for target in ("#components", "#licenses", "#offer"):
        assert f'href="{target}"' in contents
    for index in range(3):
        assert f'href="#LIC-{index}"' in contents


def test_a_licence_links_back_to_the_components_that_use_it():
    html = render(_doc(2), "html")
    assert 'href="#pkg-pkg0"' in html
    assert 'id="pkg-pkg0"' in html


def test_back_to_top_appears_only_when_the_notice_is_long():
    """Two licences fit on a screen; forty do not."""
    assert 'href="#top"' not in render(_doc(3), "html")
    assert 'href="#top"' in render(_doc(11), "html")


def test_the_licence_heading_carries_the_identifier():
    html = render(_doc(1), "html")
    assert "License 0 (LIC-0)" in html
