# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Cross-format equivalence (R-ING-3): the same package maps identically across SPDX/CycloneDX."""

from __future__ import annotations

from pathlib import Path

from onot.ingest import load_document

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "sbom"


def test_foo_equivalent_across_spdx_and_cyclonedx():
    spdx = load_document(FIX / "example.spdx.json").document
    cdx = load_document(FIX / "example.cdx.json").document

    spdx_foo = next(p for p in spdx.packages if p.name == "foo")
    cdx_foo = next(p for p in cdx.packages if p.name == "foo")

    # Core fields match, excluding format-specific fields (e.g. concluded/declared distinction)
    assert spdx_foo.name == cdx_foo.name
    assert spdx_foo.version == cdx_foo.version
    assert spdx_foo.effective_expression.raw == cdx_foo.effective_expression.raw == "MIT"
    assert spdx_foo.purl == cdx_foo.purl
    assert spdx_foo.copyright.text == cdx_foo.copyright.text


def test_both_formats_name_the_same_product():
    spdx = load_document(FIX / "example.spdx.json").document
    cdx = load_document(FIX / "example.cdx.json").document
    assert spdx.name == cdx.name == "example-product"
