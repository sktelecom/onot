"""라이선스 표현식 해석 매트릭스(R-LIC-1): 중첩/+/WITH/대소문자/unknown."""

from __future__ import annotations

import pytest

from onot.domain.errors import ExpressionParseError
from onot.license.expression_parser import symbols


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("MIT", ["MIT"]),
        ("MIT OR Apache-2.0", ["Apache-2.0", "MIT"]),
        ("MIT AND Apache-2.0", ["Apache-2.0", "MIT"]),
        ("Apache-2.0 OR (MIT AND BSD-3-Clause)", ["Apache-2.0", "BSD-3-Clause", "MIT"]),
        # 중첩 + 예외(WITH): license와 exception 심볼 분리
        (
            "(MIT OR Apache-2.0) AND GPL-2.0-only WITH Classpath-exception-2.0",
            ["Apache-2.0", "Classpath-exception-2.0", "GPL-2.0-only", "MIT"],
        ),
        # + 연산자 정규화
        ("GPL-2.0+", ["GPL-2.0-or-later"]),
        # LicenseRef 혼합
        ("MIT AND LicenseRef-Custom", ["LicenseRef-Custom", "MIT"]),
    ],
)
def test_symbols_matrix(expr, expected):
    assert sorted(symbols(expr)) == expected


def test_symbols_case_insensitive_keys():
    # license-expression은 키를 표준 형태로 정규화한다
    assert symbols("mit") == ("MIT",)


def test_symbols_unparseable_raises():
    with pytest.raises(ExpressionParseError):
        symbols(")(garbage((")
