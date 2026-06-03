# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot 도메인 모델 (순수 Pydantic v2, 외부 파서/네트워크 의존 없음).

모든 모델은 frozen=True, extra="forbid". 라이선스 표현식과 저작권은 값 객체로 구조화해
NOASSERTION/NONE을 구분한다. resolver(M2)가 LicenseExpression.symbols와
NoticeDocument.licenses를 채운다.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

_NOASSERTION = "NOASSERTION"
_NONE = "NONE"


class _Base(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PackageRef(_Base):
    """패키지 식별 참조(고지문 역참조용)."""

    name: str = Field(min_length=1)
    version: str = ""

    @property
    def display(self) -> str:
        return f"{self.name} {self.version}".strip()

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.name, self.version)


class Copyright(_Base):
    """저작권 표기. SPDX NOASSERTION/NONE을 구조적으로 구분."""

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
    """SPDX 라이선스 표현식. raw는 원본, symbols는 resolver가 평탄화해 채운다."""

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
    """문서 생성 정보. email은 SBOM 원본이 부정확할 수 있어 관대하게 str로 둔다."""

    organization: str = ""
    email: str | None = None
    source_download_url: str | None = None
    created: datetime | None = None
    creators: tuple[str, ...] = ()


class LicenseRef(_Base):
    """문서에 동봉된 커스텀/추출 라이선스."""

    identifier: str = Field(min_length=1)
    name: str | None = None
    extracted_text: str = ""


class License(_Base):
    """해석 완료된 라이선스(고지문 출력 단위). resolver가 생성."""

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
        """concluded 우선, 없으면 declared로 폴백."""
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
        """name+version 기준 중복 패키지 제거(첫 등장 보존, 순서 유지).

        주의: 이 검증은 생성/`model_validate` 시점에만 동작한다. `model_copy(update=...)`로
        packages를 교체하면 재검증되지 않으므로(Pydantic v2 동작), packages를 바꿀 때는
        새 인스턴스를 생성하거나 `model_validate`를 거쳐야 한다.
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
