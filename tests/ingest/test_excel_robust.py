# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""ExcelAdapter 견고성 — 짧은 행/빈 행/시트 누락에서 IndexError 없이 동작(L3 #1 회귀)."""

from __future__ import annotations

import openpyxl

from onot.ingest.excel import parse_excel


def _build(path, package_rows, *, with_extracted=True):
    wb = openpyxl.Workbook()
    di = wb.active
    di.title = "Document Info"
    di.append(["h"] * 6)  # 헤더(>=6열; Document Name은 index 5)
    di.append(["2.3.0", "SPDX-2.3", "CC0-1.0", "id", "3.17", "MyProduct"])
    pi = wb.create_sheet("Package Info")
    pi.append(["Package Name"])  # 헤더
    for row in package_rows:
        pi.append(row)
    if with_extracted:
        wb.create_sheet("Extracted License Info").append(["Identifier"])
    wb.save(path)


def test_short_rows_do_not_crash(tmp_path):
    path = tmp_path / "mini.xlsx"
    # name 1칸짜리 행, version까지만 채운 3칸 행 — 둘 다 16칸 미만이라
    # fixed index(12/13/16) 접근이 _cell 가드 없으면 IndexError.
    _build(path, [["foo"], ["bar", "SPDXRef-bar", "1.0"]])
    doc = parse_excel(path)
    assert doc.name == "MyProduct"
    assert [pk.name for pk in doc.packages] == ["foo", "bar"]
    foo = doc.packages[0]
    assert foo.version == ""
    assert foo.copyright is None
    assert foo.effective_expression is None
    assert doc.packages[1].version == "1.0"  # version은 컬럼 인덱스 2


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
