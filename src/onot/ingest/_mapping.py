# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""spdx-tools Document → onot.domain 매핑 헬퍼."""

from __future__ import annotations

from typing import Any

from spdx_tools.spdx.model import ActorType

from onot.domain.models import (
    Copyright,
    CreationInfo,
    LicenseExpression,
    LicenseRef,
    NoticeDocument,
    Package,
)

_MARKERS = {"NOASSERTION", "NONE", ""}


def _opt(value: object) -> str | None:
    """None/NOASSERTION/NONE은 None으로, 그 외는 문자열로."""
    if value is None:
        return None
    text = str(value).strip()
    return None if text in _MARKERS else text


def _text(value: object) -> str:
    return _opt(value) or ""


def _organization(creation_info: object) -> tuple[str, str | None]:
    for actor in getattr(creation_info, "creators", None) or []:
        if getattr(actor, "actor_type", None) == ActorType.ORGANIZATION:
            return actor.name or "", getattr(actor, "email", None)
    return "", None


def _purl(package: object) -> str | None:
    for ref in getattr(package, "external_references", None) or []:
        if getattr(ref, "reference_type", "") == "purl":
            return ref.locator
    return None


def _package(package: Any) -> Package:
    return Package(
        name=package.name,
        version=_text(getattr(package, "version", None)),
        license_concluded=LicenseExpression.from_raw(getattr(package, "license_concluded", None)),
        license_declared=LicenseExpression.from_raw(getattr(package, "license_declared", None)),
        copyright=Copyright.from_raw(getattr(package, "copyright_text", None)),
        download_location=_text(getattr(package, "download_location", None)),
        supplier=_opt(getattr(package, "supplier", None)),
        homepage=_opt(getattr(package, "homepage", None)),
        purl=_purl(package),
    )


def spdx_document_to_notice(document: Any) -> NoticeDocument:
    creation_info = document.creation_info
    organization, email = _organization(creation_info)
    creation = CreationInfo(
        organization=organization,
        email=email,
        created=getattr(creation_info, "created", None),
        creators=tuple(str(c) for c in getattr(creation_info, "creators", None) or []),
    )
    packages = tuple(_package(p) for p in getattr(document, "packages", None) or [])
    refs = tuple(
        LicenseRef(
            identifier=info.license_id,
            name=getattr(info, "license_name", None) or None,
            extracted_text=getattr(info, "extracted_text", "") or "",
        )
        for info in getattr(document, "extracted_licensing_info", None) or []
    )
    name = getattr(creation_info, "name", "") or "OSS Notice"
    return NoticeDocument(name=name, creation_info=creation, packages=packages, license_refs=refs)
