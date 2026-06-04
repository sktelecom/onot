# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot domain models (pure Pydantic v2, no external parser/network dependency).

All models are frozen=True, extra="forbid". License expressions and copyrights are
structured as value objects to distinguish NOASSERTION/NONE. The resolver (M2) fills in
LicenseExpression.symbols and NoticeDocument.licenses.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

_NOASSERTION = "NOASSERTION"
_NONE = "NONE"


class _Base(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PackageRef(_Base):
    """Package identity reference (for back-references in the notice)."""

    name: str = Field(min_length=1)
    version: str = ""

    @property
    def display(self) -> str:
        return f"{self.name} {self.version}".strip()

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.name, self.version)


class Copyright(_Base):
    """Copyright notice. Structurally distinguishes SPDX NOASSERTION/NONE."""

    text: str = ""
    is_noassertion: bool = False
    is_none: bool = False

    @classmethod
    def from_raw(cls, value: object) -> Copyright | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        if text == _NOASSERTION:
            return cls(text="", is_noassertion=True)
        if text == _NONE:
            return cls(text="", is_none=True)
        return cls(text=text)

    @property
    def display(self) -> str:
        return self.text


class LicenseExpression(_Base):
    """SPDX license expression. raw is the original; symbols are flattened and filled by the resolver."""

    raw: str = Field(min_length=1)
    symbols: tuple[str, ...] = ()

    @classmethod
    def from_raw(cls, value: object) -> LicenseExpression | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text in {_NOASSERTION, _NONE}:
            return None
        return cls(raw=text)

    def __str__(self) -> str:
        return self.raw


class CreationInfo(_Base):
    """Document creation info. email is kept lenient as str since the source SBOM may be inaccurate."""

    organization: str = ""
    email: str | None = None
    source_download_url: str | None = None
    created: datetime | None = None
    creators: tuple[str, ...] = ()


class LicenseRef(_Base):
    """Custom/extracted license embedded in the document."""

    identifier: str = Field(min_length=1)
    name: str | None = None
    extracted_text: str = ""


class License(_Base):
    """Resolved license (a notice output unit). Created by the resolver."""

    license_id: str = Field(min_length=1)
    name: str = ""
    is_exception: bool = False
    is_deprecated: bool = False
    text: str = ""
    reference_url: str | None = None
    used_by: tuple[PackageRef, ...] = ()


class Package(_Base):
    name: str = Field(min_length=1)
    version: str = ""
    license_concluded: LicenseExpression | None = None
    license_declared: LicenseExpression | None = None
    copyright: Copyright | None = None
    download_location: str = ""
    supplier: str | None = None
    homepage: str | None = None
    purl: str | None = None

    @property
    def effective_expression(self) -> LicenseExpression | None:
        """Prefer concluded; fall back to declared if absent."""
        return self.license_concluded or self.license_declared

    @property
    def ref(self) -> PackageRef:
        return PackageRef(name=self.name, version=self.version)

    @property
    def display(self) -> str:
        return self.ref.display

    @property
    def expression_display(self) -> str:
        expr = self.effective_expression
        return expr.raw if expr is not None else ""

    @property
    def copyright_display(self) -> str:
        return self.copyright.display if self.copyright is not None else ""


class NoticeDocument(_Base):
    name: str = Field(min_length=1)
    creation_info: CreationInfo = CreationInfo()
    packages: tuple[Package, ...] = ()
    license_refs: tuple[LicenseRef, ...] = ()
    licenses: tuple[License, ...] = ()

    @model_validator(mode="after")
    def _dedup_packages(self) -> NoticeDocument:
        """Remove duplicate packages by name+version (keep first occurrence, preserve order).

        Note: this validation runs only at construction/`model_validate` time. Replacing
        packages via `model_copy(update=...)` does not re-validate (Pydantic v2 behavior),
        so to change packages you must create a new instance or go through `model_validate`.
        """
        seen: set[tuple[str, str]] = set()
        unique: list[Package] = []
        for pkg in self.packages:
            key = (pkg.name, pkg.version)
            if key in seen:
                continue
            seen.add(key)
            unique.append(pkg)
        if len(unique) != len(self.packages):
            object.__setattr__(self, "packages", tuple(unique))
        return self
