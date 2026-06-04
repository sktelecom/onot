# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Bundled SPDX license-list-data catalog (includes full texts, fully air-gapped).

The data is vendored via `scripts/update_license_data.py`. For frozen-environment safety,
it is accessed through importlib.resources '/' chaining (D-006).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files


@dataclass(frozen=True)
class CatalogEntry:
    license_id: str
    name: str
    text: str
    is_exception: bool
    is_deprecated: bool
    reference_url: str | None


class SpdxLicenseCatalog:
    def __init__(self, data: dict) -> None:
        self.version: str = data.get("licenseListVersion", "")
        self._licenses: dict[str, dict] = data.get("licenses", {})
        self._exceptions: dict[str, dict] = data.get("exceptions", {})

    @classmethod
    def bundled(cls) -> SpdxLicenseCatalog:
        return _bundled_catalog()

    def get(self, license_id: str) -> CatalogEntry | None:
        entry = self._licenses.get(license_id)
        if entry is not None:
            return self._entry(license_id, entry, is_exception=False)
        entry = self._exceptions.get(license_id)
        if entry is not None:
            return self._entry(license_id, entry, is_exception=True)
        return None

    @staticmethod
    def _entry(license_id: str, raw: dict, *, is_exception: bool) -> CatalogEntry:
        return CatalogEntry(
            license_id=license_id,
            name=raw.get("name", ""),
            text=raw.get("text", ""),
            is_exception=is_exception,
            is_deprecated=bool(raw.get("deprecated", False)),
            reference_url=raw.get("reference"),
        )

    def __contains__(self, license_id: object) -> bool:
        return license_id in self._licenses or license_id in self._exceptions

    def __len__(self) -> int:
        return len(self._licenses) + len(self._exceptions)


@lru_cache(maxsize=1)
def _bundled_catalog() -> SpdxLicenseCatalog:
    resource = files("onot.license") / "data" / "licenses.json"
    data = json.loads(resource.read_text(encoding="utf-8"))
    return SpdxLicenseCatalog(data)
