# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""LicenseResolver: air-gapped full-text fill, embedded ref, unknown, cache, remote fetch."""

from __future__ import annotations

import httpx
import pytest
import respx

from onot.domain.errors import UnknownLicenseError
from onot.domain.models import LicenseExpression, LicenseRef, NoticeDocument, Package
from onot.license.cache import DiskCache
from onot.license.catalog import SpdxLicenseCatalog
from onot.license.fetcher import RemoteLicenseFetcher
from onot.license.resolver import LicenseResolver

URL = "https://spdx.org/licenses"


def _doc(expr=None, refs=()):
    packages = ()
    if expr is not None:
        packages = (Package(name="p", version="1", license_concluded=LicenseExpression(raw=expr)),)
    return NoticeDocument(name="prod", packages=packages, license_refs=refs)


def test_airgap_fills_text_from_bundle_offline():
    # Fill full text from the bundle without network (offline, no fetcher)
    res = LicenseResolver().resolve(_doc("MIT"))
    lic = res.document.licenses[0]
    assert lic.license_id == "MIT"
    assert "Permission is hereby granted" in lic.text
    assert res.warnings == ()


def test_custom_ref_text_used():
    refs = (LicenseRef(identifier="LicenseRef-X", name="My X", extracted_text="CUSTOM"),)
    res = LicenseResolver().resolve(_doc("LicenseRef-X", refs))
    lic = res.document.licenses[0]
    assert (lic.license_id, lic.name, lic.text) == ("LicenseRef-X", "My X", "CUSTOM")


def test_exception_split_with_text():
    res = LicenseResolver().resolve(_doc("GPL-2.0-only WITH Classpath-exception-2.0"))
    ids = [lic.license_id for lic in res.document.licenses]
    assert ids == ["Classpath-exception-2.0", "GPL-2.0-only"]
    exc = next(lic for lic in res.document.licenses if lic.is_exception)
    assert exc.text


def test_unknown_lenient_warns():
    res = LicenseResolver(offline=True).resolve(_doc("Definitely-Not-A-License-1.0"))
    assert any("unknown license" in w for w in res.warnings)
    assert res.document.licenses[0].text == ""


def test_unknown_strict_raises():
    with pytest.raises(UnknownLicenseError):
        LicenseResolver(offline=True, strict=True).resolve(_doc("Definitely-Not-A-License-1.0"))


def test_cache_hit_offline(tmp_path):
    cache = DiskCache("v", base_dir=tmp_path)
    cache.set("Future-License-1.0", "FUTURE TEXT")
    res = LicenseResolver(offline=True, cache=cache).resolve(_doc("Future-License-1.0"))
    assert res.document.licenses[0].text == "FUTURE TEXT"
    assert res.warnings == ()


@respx.mock
def test_online_fetch_for_uncatalogued(tmp_path):
    respx.get(f"{URL}/Future-License-1.0.json").mock(
        return_value=httpx.Response(200, json={"licenseText": "NET TEXT"})
    )
    cache = DiskCache("v", base_dir=tmp_path)
    resolver = LicenseResolver(offline=False, cache=cache, fetcher=RemoteLicenseFetcher(backoff=0))
    res = resolver.resolve(_doc("Future-License-1.0"))
    assert res.document.licenses[0].text == "NET TEXT"
    assert cache.get("Future-License-1.0") == "NET TEXT"  # written to cache


def test_unparseable_expression_warns_and_keeps_raw():
    res = LicenseResolver(offline=True).resolve(_doc(")(garbage(("))
    assert any("unparseable expression" in w for w in res.warnings)


def test_deprecated_and_reference_propagated():
    # Directly verify is_deprecated/reference_url propagate from catalog -> License (M4 renderer dependency).
    # (Real SPDX deprecated ids get canonicalized by license-expression, so a custom catalog is used)
    catalog = SpdxLicenseCatalog(
        {
            "licenseListVersion": "x",
            "licenses": {
                "Dep-1.0": {
                    "name": "Dep",
                    "text": "t",
                    "reference": "http://ref",
                    "deprecated": True,
                }
            },
            "exceptions": {},
        }
    )
    res = LicenseResolver(catalog=catalog, offline=True).resolve(_doc("Dep-1.0"))
    lic = res.document.licenses[0]
    assert lic.license_id == "Dep-1.0"
    assert lic.is_deprecated is True
    assert lic.reference_url == "http://ref"


def test_catalog_entry_empty_text_falls_back_to_cache(tmp_path):
    # When the catalog has an entry but its text is empty, fall back to cache/remote (resolver defensive branch)
    catalog = SpdxLicenseCatalog(
        {
            "licenseListVersion": "x",
            "licenses": {"Foo-1.0": {"name": "Foo", "text": "", "reference": "r"}},
            "exceptions": {},
        }
    )
    cache = DiskCache("v", base_dir=tmp_path)
    cache.set("Foo-1.0", "CACHED FOO")
    res = LicenseResolver(catalog=catalog, cache=cache, offline=True).resolve(_doc("Foo-1.0"))
    lic = res.document.licenses[0]
    assert lic.name == "Foo"
    assert lic.text == "CACHED FOO"


@respx.mock
def test_offline_never_fetches_even_with_fetcher():
    # respx.mock active + no route registered: a real call would error. With offline, zero calls is required to pass.
    resolver = LicenseResolver(offline=True, fetcher=RemoteLicenseFetcher(backoff=0))
    res = resolver.resolve(_doc("Definitely-Not-A-License-1.0"))
    assert any("unknown license" in w for w in res.warnings)
