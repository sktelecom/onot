# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""LicenseResolver — orchestrates expression resolution + full-text lookup.

Flattens each package's effective_expression to build the license list and back-references
(used_by), then fills full texts in the order: bundled catalog -> disk cache -> (when online)
remote fetch. An embedded LicenseRef uses its extracted_text as the full text.
"""

from __future__ import annotations

from dataclasses import dataclass

from onot.domain.errors import ExpressionParseError, UnknownLicenseError
from onot.domain.models import License, NoticeDocument, PackageRef
from onot.license.cache import DiskCache
from onot.license.catalog import SpdxLicenseCatalog
from onot.license.expression_parser import symbols
from onot.license.fetcher import RemoteLicenseFetcher


@dataclass(frozen=True)
class ResolveResult:
    document: NoticeDocument
    warnings: tuple[str, ...]


class LicenseResolver:
    """The injected fetcher's lifecycle (httpx client close) is the caller's responsibility (the resolver does not close it)."""

    def __init__(
        self,
        *,
        catalog: SpdxLicenseCatalog | None = None,
        cache: DiskCache | None = None,
        fetcher: RemoteLicenseFetcher | None = None,
        offline: bool = True,
        strict: bool = False,
    ) -> None:
        self.catalog = catalog or SpdxLicenseCatalog.bundled()
        self.cache = cache
        self.fetcher = fetcher
        self.offline = offline
        self.strict = strict

    def resolve(self, doc: NoticeDocument) -> ResolveResult:
        ref_text = {r.identifier: r.extracted_text for r in doc.license_refs}
        ref_name = {r.identifier: (r.name or r.identifier) for r in doc.license_refs}
        warnings: list[str] = []

        used: dict[str, list[PackageRef]] = {}
        for pkg in doc.packages:
            expr = pkg.effective_expression
            if expr is None:
                continue
            try:
                syms = symbols(expr.raw)
            except ExpressionParseError:
                warnings.append(f"unparseable expression for {pkg.display}: {expr.raw}")
                syms = (expr.raw,)
            ref = pkg.ref
            for symbol in syms:
                holders = used.setdefault(symbol, [])
                if ref not in holders:
                    holders.append(ref)

        licenses = tuple(
            self._build_license(lid, tuple(used[lid]), ref_text, ref_name, warnings)
            for lid in sorted(used)
        )
        document = doc.model_copy(update={"licenses": licenses})
        return ResolveResult(document=document, warnings=tuple(warnings))

    def _build_license(
        self,
        license_id: str,
        used_by: tuple[PackageRef, ...],
        ref_text: dict[str, str],
        ref_name: dict[str, str],
        warnings: list[str],
    ) -> License:
        entry = self.catalog.get(license_id)
        if entry is not None:
            text = entry.text or self._lookup_remote(license_id, is_exception=entry.is_exception)
            return License(
                license_id=license_id,
                name=entry.name or license_id,
                is_exception=entry.is_exception,
                is_deprecated=entry.is_deprecated,
                text=text or "",
                reference_url=entry.reference_url,
                used_by=used_by,
            )
        if license_id in ref_text:
            return License(
                license_id=license_id,
                name=ref_name.get(license_id, license_id),
                text=ref_text[license_id],
                used_by=used_by,
            )
        # Found neither in the catalog nor embedded: supplement remotely if online, otherwise unknown
        text = self._lookup_remote(license_id, is_exception=False)
        if text:
            return License(license_id=license_id, name=license_id, text=text, used_by=used_by)
        message = f"unknown license: {license_id}"
        if self.strict:
            raise UnknownLicenseError(message)
        warnings.append(message)
        return License(license_id=license_id, name=license_id, text="", used_by=used_by)

    def _lookup_remote(self, license_id: str, *, is_exception: bool) -> str | None:
        if self.cache is not None:
            cached = self.cache.get(license_id)
            if cached is not None:
                return cached
        if self.offline or self.fetcher is None:
            return None
        text = self.fetcher.fetch_text(license_id, is_exception=is_exception)
        if text and self.cache is not None:
            self.cache.set(license_id, text)
        return text
