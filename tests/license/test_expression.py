# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""License expression resolution matrix (R-LIC-1): nesting/+/WITH/case/unknown."""

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
        # Nesting + exception (WITH): license and exception symbols separated
        (
            "(MIT OR Apache-2.0) AND GPL-2.0-only WITH Classpath-exception-2.0",
            ["Apache-2.0", "Classpath-exception-2.0", "GPL-2.0-only", "MIT"],
        ),
        # + operator normalization
        ("GPL-2.0+", ["GPL-2.0-or-later"]),
        # Mixed LicenseRef
        ("MIT AND LicenseRef-Custom", ["LicenseRef-Custom", "MIT"]),
    ],
)
def test_symbols_matrix(expr, expected):
    assert sorted(symbols(expr)) == expected


def test_symbols_case_insensitive_keys():
    # license-expression normalizes keys to their canonical form
    assert symbols("mit") == ("MIT",)


def test_symbols_unparseable_raises():
    with pytest.raises(ExpressionParseError):
        symbols(")(garbage((")
