# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""M1 domain model unit tests: validation rules, value objects, deduplication, determinism."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from onot.domain.models import (
    Copyright,
    License,
    LicenseExpression,
    NoticeDocument,
    Package,
    PackageRef,
)


# --- PackageRef ---------------------------------------------------------------
def test_package_ref_display_and_sortkey():
    ref = PackageRef(name="foo", version="1.2")
    assert ref.display == "foo 1.2"
    assert ref.sort_key == ("foo", "1.2")
    assert PackageRef(name="bar").display == "bar"


# --- Copyright ----------------------------------------------------------------
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("", None),
        ("   ", None),
        ("NOASSERTION", Copyright(text="", is_noassertion=True)),
        ("NONE", Copyright(text="", is_none=True)),
        ("Copyright 2024 X", Copyright(text="Copyright 2024 X")),
    ],
)
def test_copyright_from_raw(raw, expected):
    assert Copyright.from_raw(raw) == expected


def test_copyright_display():
    assert Copyright.from_raw("NOASSERTION").display == ""
    assert Copyright(text="abc").display == "abc"


# --- LicenseExpression --------------------------------------------------------
@pytest.mark.parametrize("raw", [None, "", "  ", "NOASSERTION", "NONE"])
def test_license_expression_from_raw_none(raw):
    assert LicenseExpression.from_raw(raw) is None


def test_license_expression_from_raw_value():
    expr = LicenseExpression.from_raw("  MIT OR Apache-2.0 ")
    assert expr == LicenseExpression(raw="MIT OR Apache-2.0")
    assert str(expr) == "MIT OR Apache-2.0"


def test_license_expression_blank_raw_rejected():
    with pytest.raises(ValidationError):
        LicenseExpression(raw="")


# --- Package ------------------------------------------------------------------
def test_package_effective_expression_fallback():
    declared = LicenseExpression(raw="Apache-2.0")
    concluded = LicenseExpression(raw="MIT")
    assert (
        Package(
            name="p", license_concluded=concluded, license_declared=declared
        ).effective_expression
        == concluded
    )
    assert Package(name="p", license_declared=declared).effective_expression == declared
    assert Package(name="p").effective_expression is None


def test_package_displays_and_ref():
    pkg = Package(
        name="p",
        version="1.0",
        license_declared=LicenseExpression(raw="MIT"),
        copyright=Copyright(text="Copyright X"),
    )
    assert pkg.ref == PackageRef(name="p", version="1.0")
    assert pkg.display == "p 1.0"
    assert pkg.expression_display == "MIT"
    assert pkg.copyright_display == "Copyright X"
    assert Package(name="p").expression_display == ""
    assert Package(name="p").copyright_display == ""


def test_package_empty_name_rejected():
    with pytest.raises(ValidationError):
        Package(name="")


def test_extra_field_forbidden():
    with pytest.raises(ValidationError):
        Package(name="p", bogus=1)


def test_frozen_immutability():
    pkg = Package(name="p")
    with pytest.raises(ValidationError):
        pkg.name = "q"


# --- NoticeDocument -----------------------------------------------------------
def test_dedup_packages_preserves_first_and_order():
    a1 = Package(name="a", version="1")
    a1_dup = Package(name="a", version="1", download_location="x")
    b = Package(name="b", version="2")
    a2 = Package(name="a", version="2")
    doc = NoticeDocument(name="prod", packages=(a1, b, a1_dup, a2))
    # a/1 deduplicated (first occurrence kept), order preserved
    assert [(p.name, p.version) for p in doc.packages] == [("a", "1"), ("b", "2"), ("a", "2")]
    assert doc.packages[0] is a1  # first occurrence kept


def test_document_requires_name():
    with pytest.raises(ValidationError):
        NoticeDocument(name="")


def _sample_doc():
    return NoticeDocument(
        name="prod",
        packages=(
            Package(name="a", version="1", license_declared=LicenseExpression(raw="MIT")),
            Package(name="b", version="2"),
        ),
        licenses=(License(license_id="MIT", used_by=(PackageRef(name="a", version="1"),)),),
    )


def test_serialization_deterministic():
    # Serialization of two independently but identically constructed documents matches (not self-comparison)
    assert _sample_doc().model_dump_json() == _sample_doc().model_dump_json()


def test_dedup_runs_on_model_validate_roundtrip():
    # Pin that dedup also runs on a model_validate roundtrip (same contract as construction-time validation)
    a = Package(name="a", version="1")
    dup = Package(name="a", version="1", download_location="x")
    payload = NoticeDocument.model_construct(name="prod", packages=(a, dup)).model_dump()
    revalidated = NoticeDocument.model_validate(payload)
    assert [(p.name, p.version) for p in revalidated.packages] == [("a", "1")]
