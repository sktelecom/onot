# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""레지스트리: 어댑터 목록, load_document end-to-end."""

from __future__ import annotations

from pathlib import Path

from onot.ingest.registry import available_formats, load_document

ROOT = Path(__file__).resolve().parents[2]


def test_available_formats():
    assert set(available_formats()) == {"spdx", "cyclonedx", "excel"}


def test_load_document_excel_end_to_end():
    res = load_document(ROOT / "tests" / "fixtures" / "sbom" / "example.spdx.xlsx")
    assert res.document.name
    assert res.document.packages
