"""SPDX 라이선스 표현식 파싱(license-expression 래퍼).

중첩 OR/AND/WITH와 + 연산자를 평탄화해 심볼을 추출한다. 파싱 실패는
ExpressionParseError로 올린다(resolver가 폴백 처리).
"""

from __future__ import annotations

from functools import lru_cache

from license_expression import Licensing, get_spdx_licensing

from onot.domain.errors import ExpressionParseError


@lru_cache(maxsize=1)
def _licensing() -> Licensing:
    return get_spdx_licensing()


def symbols(expression: str) -> tuple[str, ...]:
    """표현식의 모든 license/exception 심볼을 중복 없이 평탄화해 반환."""
    licensing = _licensing()
    try:
        parsed = licensing.parse(expression)
    except Exception as exc:  # noqa: BLE001 — 라이브러리 예외를 도메인 예외로 래핑
        raise ExpressionParseError(f"invalid license expression: {expression!r}") from exc
    return tuple(str(s) for s in licensing.license_symbols(parsed, unique=True, decompose=True))
