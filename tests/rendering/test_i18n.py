# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""i18n consistency: catalog loads, missing-key handling, language fallback."""

from __future__ import annotations

from onot.rendering.i18n import AVAILABLE_LANGS, Translator, _catalog


def test_catalog_nonempty():
    for lang in AVAILABLE_LANGS:
        assert _catalog(lang)


def test_missing_key_returns_key():
    assert Translator("en")("no.such.key") == "no.such.key"


def test_format_interpolation():
    assert Translator("en")("notice.title", product="X") == "OSS Notice for X"


def test_unknown_lang_falls_back_to_en():
    assert Translator("zz").lang == "en"
