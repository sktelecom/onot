"""i18n 정합성: ko/en 키·플레이스홀더 동일, 누락 키 처리, 폴백."""

from __future__ import annotations

import re

from onot.rendering.i18n import Translator, _catalog


def _placeholders(text: str) -> set[str]:
    return set(re.findall(r"{(\w+)}", text))


def test_key_parity():
    assert set(_catalog("en")) == set(_catalog("ko"))


def test_placeholder_parity():
    en, ko = _catalog("en"), _catalog("ko")
    for key in en:
        assert _placeholders(en[key]) == _placeholders(ko[key]), key


def test_missing_key_returns_key():
    assert Translator("en")("no.such.key") == "no.such.key"


def test_format_interpolation():
    assert Translator("en")("notice.title", product="X") == "OSS Notice for X"
    assert Translator("ko")("notice.title", product="X") == "X 오픈소스 고지"


def test_unknown_lang_falls_back_to_en():
    assert Translator("zz").lang == "en"
