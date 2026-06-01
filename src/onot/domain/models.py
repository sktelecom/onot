"""onot 도메인 모델.

M0.5 수직 슬라이스 단계의 최소 모델. M1에서 LicenseExpression 값 객체, Copyright의
NOASSERTION/NONE 구분, CreationInfo, PackageRef 등으로 확장된다. 라이선스 표현식은
현재 원본 문자열로 보관하며 M1에서 LicenseExpression으로 승격한다.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Package(_Base):
    name: str
    version: str = ""
    license_concluded: str | None = None
    license_declared: str | None = None
    copyright: str | None = None
    download_location: str = ""

    @property
    def effective_expression(self) -> str | None:
        """concluded 우선, 없으면 declared로 폴백."""
        return self.license_concluded or self.license_declared

    @property
    def display(self) -> str:
        return f"{self.name} {self.version}".strip()


class LicenseRef(_Base):
    """문서에 동봉된 커스텀/추출 라이선스."""

    identifier: str
    name: str | None = None
    extracted_text: str = ""


class License(_Base):
    """해석 완료된 라이선스(고지문 출력 단위)."""

    license_id: str
    name: str = ""
    text: str = ""
    used_by: tuple[str, ...] = ()


class NoticeDocument(_Base):
    name: str
    packages: tuple[Package, ...] = ()
    license_refs: tuple[LicenseRef, ...] = ()
    licenses: tuple[License, ...] = ()
