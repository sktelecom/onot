# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Bundled SPDX catalog (part of R-LIC-2): includes full text, license/exception lookup."""

from __future__ import annotations

from onot.license.catalog import SpdxLicenseCatalog


def test_bundled_has_common_licenses_with_text():
    cat = SpdxLicenseCatalog.bundled()
    assert cat.version  # e.g. 3.28.0
    assert len(cat) > 700
    mit = cat.get("MIT")
    assert mit is not None
    assert not mit.is_exception
    assert "Permission is hereby granted" in mit.text
    assert cat.get("Apache-2.0").name == "Apache License 2.0"


def test_bundled_has_exceptions():
    cat = SpdxLicenseCatalog.bundled()
    exc = cat.get("Classpath-exception-2.0")
    assert exc is not None
    assert exc.is_exception
    assert exc.text


def test_contains_and_unknown():
    cat = SpdxLicenseCatalog.bundled()
    assert "MIT" in cat
    assert "Classpath-exception-2.0" in cat
    assert "NoSuchLicense-9.9" not in cat
    assert cat.get("NoSuchLicense-9.9") is None


def test_from_dict():
    cat = SpdxLicenseCatalog(
        {
            "licenseListVersion": "9.9",
            "licenses": {"X": {"name": "X License", "text": "t", "reference": "u"}},
            "exceptions": {},
        }
    )
    entry = cat.get("X")
    assert entry.name == "X License"
    assert entry.reference_url == "u"
    assert not entry.is_deprecated
