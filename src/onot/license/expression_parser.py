# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""SPDX license expression parsing (wrapper around license-expression).

Flattens nested OR/AND/WITH and the + operator to extract symbols. Parse failures are
raised as ExpressionParseError (the resolver handles the fallback).
"""

from __future__ import annotations

from functools import lru_cache

from license_expression import Licensing, get_spdx_licensing

from onot.domain.errors import ExpressionParseError


@lru_cache(maxsize=1)
def _licensing() -> Licensing:
    return get_spdx_licensing()


def symbols(expression: str) -> tuple[str, ...]:
    """Return all license/exception symbols of the expression, flattened and deduplicated."""
    licensing = _licensing()
    try:
        parsed = licensing.parse(expression)
    except Exception as exc:  # noqa: BLE001 — wrap the library exception as a domain exception
        raise ExpressionParseError(f"invalid license expression: {expression!r}") from exc
    return tuple(str(s) for s in licensing.license_symbols(parsed, unique=True, decompose=True))
