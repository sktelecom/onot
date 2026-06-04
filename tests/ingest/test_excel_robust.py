# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""ExcelAdapter robustness - works without IndexError on short rows/blank rows/missing sheets (L3 #1 regression)."""

from __future__ import annotations

import openpyxl

from onot.ingest.excel import parse_excel


def _build(path, package_rows, *, with_extracted=True):
    wb = openpyxl.Workbook()
    di = wb.active
    di.title = "Document Info"
    di.append(["h"] * 6)  # header (>=6 columns; Document Name is index 5)
    di.append(["2.3.0", "SPDX-2.3", "CC0-1.0", "id", "3.17", "MyProduct"])
    pi = wb.create_sheet("Package Info")
    pi.append(["Package Name"])  # header
    for row in package_rows:
        pi.append(row)
    if with_extracted:
        wb.create_sheet("Extracted License Info").append(["Identifier"])
    wb.save(path)


def test_short_rows_do_not_crash(tmp_path):
    path = tmp_path / "mini.xlsx"
    # A 1-cell row (name only) and a 3-cell row (up to version) - both under 16 cells, so
    # fixed-index (12/13/16) access raises IndexError without the _cell guard.
    _build(path, [["foo"], ["bar", "SPDXRef-bar", "1.0"]])
    doc = parse_excel(path)
    assert doc.name == "MyProduct"
    assert [pk.name for pk in doc.packages] == ["foo", "bar"]
    foo = doc.packages[0]
    assert foo.version == ""
    assert foo.copyright is None
    assert foo.effective_expression is None
    assert doc.packages[1].version == "1.0"  # version is column index 2


def test_missing_extracted_sheet(tmp_path):
    path = tmp_path / "noext.xlsx"
    _build(path, [["foo"]], with_extracted=False)
    doc = parse_excel(path)
    assert doc.license_refs == ()


def test_blank_rows_skipped(tmp_path):
    path = tmp_path / "blank.xlsx"
    _build(path, [[None], ["", None], ["keep"]])
    doc = parse_excel(path)
    assert [pk.name for pk in doc.packages] == ["keep"]
