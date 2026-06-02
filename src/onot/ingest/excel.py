"""ExcelAdapter — 1.x onot/SPDX 스프레드시트 템플릿 → NoticeDocument.

Document Info, Package Info, Extracted License Info 시트를 읽어 NoticeDocument로 매핑한다.
ExcelAdapter로 registry에 통합된다. 컬럼 인덱스는 표준 SPDX 스프레드시트 스키마 기준이다.
"""

from __future__ import annotations

from pathlib import Path

import openpyxl

from onot.domain.models import Copyright, LicenseExpression, LicenseRef, NoticeDocument, Package
from onot.ingest.base import IngestResult

# 표준 SPDX 스프레드시트 컬럼 인덱스(0-base)
_DOC_NAME_COL = 5
_PKG_COLS = {
    "name": 0,
    "version": 2,
    "download": 7,
    "declared": 12,
    "concluded": 13,
    "copyright": 16,
}
_EXT_COLS = {"id": 0, "text": 1, "name": 2}


class ExcelAdapter:
    format_id = "excel"

    def sniff(self, path: Path, head: bytes) -> float:
        if path.name.lower().endswith((".xlsx", ".xls")):
            return 0.8
        if head.startswith(b"PK\x03\x04"):  # xlsx = zip
            return 0.4
        return 0.0

    def parse(self, path: Path) -> IngestResult:
        return IngestResult(document=parse_excel(path))


def _cell(row: tuple, index: int) -> object:
    """짧은 행/빈 행에서도 안전한 셀 접근(없으면 None)."""
    if not row or index >= len(row):
        return None
    return row[index]


def _clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _none_if_blank(value: object) -> str | None:
    text = _clean(value)
    return text or None


def parse_excel(path: str | Path) -> NoticeDocument:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        name = _document_name(wb)
        packages = _packages(wb)
        refs = _extracted_licenses(wb)
    finally:
        wb.close()
    return NoticeDocument(name=name, packages=tuple(packages), license_refs=tuple(refs))


def _document_name(wb: openpyxl.Workbook) -> str:
    ws = wb["Document Info"]
    rows = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))
    if rows:
        return _clean(_cell(rows[0], _DOC_NAME_COL)) or "OSS Notice"
    return "OSS Notice"


def _packages(wb: openpyxl.Workbook) -> list[Package]:
    ws = wb["Package Info"]
    out: list[Package] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = _clean(_cell(row, _PKG_COLS["name"]))
        if not name:
            continue
        out.append(
            Package(
                name=name,
                version=_clean(_cell(row, _PKG_COLS["version"])),
                license_concluded=LicenseExpression.from_raw(_cell(row, _PKG_COLS["concluded"])),
                license_declared=LicenseExpression.from_raw(_cell(row, _PKG_COLS["declared"])),
                copyright=Copyright.from_raw(_cell(row, _PKG_COLS["copyright"])),
                download_location=_clean(_cell(row, _PKG_COLS["download"])),
            )
        )
    return out


def _extracted_licenses(wb: openpyxl.Workbook) -> list[LicenseRef]:
    if "Extracted License Info" not in wb.sheetnames:
        return []
    ws = wb["Extracted License Info"]
    out: list[LicenseRef] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        identifier = _clean(_cell(row, _EXT_COLS["id"]))
        if not identifier:
            continue
        out.append(
            LicenseRef(
                identifier=identifier,
                name=_none_if_blank(_cell(row, _EXT_COLS["name"])),
                extracted_text=_clean(_cell(row, _EXT_COLS["text"])),
            )
        )
    return out
