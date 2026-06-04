# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Disk cache (R-LIC-3): hit/miss, corruption tolerance."""

from __future__ import annotations

from onot.license.cache import DiskCache


def test_set_get_roundtrip(tmp_path):
    cache = DiskCache("licenses-3.28.0", base_dir=tmp_path)
    assert cache.get("MIT") is None
    cache.set("MIT", "the text")
    assert cache.get("MIT") == "the text"


def test_namespaces_isolated(tmp_path):
    a = DiskCache("v1", base_dir=tmp_path)
    b = DiskCache("v2", base_dir=tmp_path)
    a.set("MIT", "old")
    assert b.get("MIT") is None  # isolated by version namespace (natural invalidation)


def test_missing_dir_returns_none(tmp_path):
    cache = DiskCache("nope", base_dir=tmp_path / "absent")
    assert cache.get("anything") is None
