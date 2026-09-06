# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Builds the render context. Merges company settings with SBOM values (company settings take precedence; fall back to SBOM when empty)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from onot import __version__
from onot.core.config import Settings
from onot.domain.models import NoticeDocument


@dataclass(frozen=True)
class RenderContext:
    document: NoticeDocument
    product: str
    organization: str
    email: str
    copyright_holder: str
    copyright_year: int | None
    source_url: str
    generated: str
    license_ids: tuple[str, ...]
    tool_version: str


def _first(*values: str) -> str:
    for value in values:
        if value:
            return value
    return ""


def build_context(
    doc: NoticeDocument,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> RenderContext:
    company = settings.company
    creation = doc.creation_info
    year = company.copyright_year
    if year is None and creation.created is not None:
        year = creation.created.year
    return RenderContext(
        document=doc,
        product=doc.name,
        organization=_first(company.organization, creation.organization),
        email=_first(company.contact_email, creation.email or ""),
        copyright_holder=_first(
            company.copyright_holder, company.organization, creation.organization
        ),
        copyright_year=year,
        source_url=_first(company.source_download_url, creation.source_download_url or ""),
        generated=now.strftime("%Y-%m-%d") if now is not None else "",
        license_ids=tuple(lic.license_id for lic in doc.licenses),
        # Recorded in the notice footer so a reviewer can tell which build produced the file.
        tool_version=__version__,
    )
