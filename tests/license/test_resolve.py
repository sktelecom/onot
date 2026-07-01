# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""License resolver determinism test (R-DOM-2/R-LIC)."""

from __future__ import annotations

from onot.domain.models import LicenseExpression, LicenseRef, NoticeDocument, Package
from onot.license import resolve, resolve_with_warnings


def _doc():
    return NoticeDocument(
        name="prod",
        packages=(
            Package(name="z", version="1", license_concluded=LicenseExpression(raw="MIT")),
            Package(
                name="a",
                version="2",
                license_declared=LicenseExpression(raw="MIT OR Apache-2.0"),
            ),
        ),
    )


def test_resolve_deterministic_and_sorted():
    r1 = resolve(_doc())
    r2 = resolve(_doc())
    assert r1.licenses == r2.licenses
    ids = [lic.license_id for lic in r1.licenses]
    assert ids == sorted(ids)  # licenses sorted by id (deterministic)
    # used_by preserves package appearance order (deterministic)
    mit = next(lic for lic in r1.licenses if lic.license_id == "MIT")
    assert [r.display for r in mit.used_by] == ["z 1", "a 2"]


def test_resolve_skips_packages_without_license():
    doc = NoticeDocument(name="p", packages=(Package(name="x"),))
    assert resolve(doc).licenses == ()


def test_resolve_warns_on_missing_license_information():
    # O-9: a package with no license info must surface a warning, not pass silently.
    doc = NoticeDocument(name="p", packages=(Package(name="x", version="1"),))
    warnings = resolve_with_warnings(doc).warnings
    assert any("no license information for x 1" in w for w in warnings)


def test_resolve_warns_on_empty_license_ref_text():
    # O-9: a referenced LicenseRef with blank extracted text yields an empty section -> warn.
    doc = NoticeDocument(
        name="p",
        packages=(
            Package(name="x", version="1", license_concluded=LicenseExpression(raw="LicenseRef-1")),
        ),
        license_refs=(LicenseRef(identifier="LicenseRef-1", extracted_text=""),),
    )
    result = resolve_with_warnings(doc)
    assert any("missing license text for LicenseRef-1" in w for w in result.warnings)
