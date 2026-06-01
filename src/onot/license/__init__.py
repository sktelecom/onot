"""라이선스 해석 (M0.5 슬라이스 최소 구현).

각 패키지의 effective_expression을 license-expression으로 평탄화해 라이선스 목록과
역참조(used_by)를 만든다. 전문(text)은 동봉 LicenseRef에서만 채우고, SPDX 카탈로그
번들/캐시/오프라인 fetch는 M2에서 추가한다.
"""

from __future__ import annotations

from license_expression import get_spdx_licensing

from onot.domain.models import License, NoticeDocument

_licensing = get_spdx_licensing()


def _symbols(expression: str) -> list[str]:
    try:
        parsed = _licensing.parse(expression)
        return [str(s) for s in _licensing.license_symbols(parsed, unique=True, decompose=True)]
    except Exception:  # noqa: BLE001 — 슬라이스: 파싱 불가 표현식은 원문 그대로
        return [expression]


def resolve(doc: NoticeDocument) -> NoticeDocument:
    ref_text = {r.identifier: r.extracted_text for r in doc.license_refs}
    ref_name = {r.identifier: (r.name or r.identifier) for r in doc.license_refs}

    used: dict[str, list[str]] = {}
    for pkg in doc.packages:
        expression = pkg.effective_expression
        if not expression:
            continue
        for symbol in _symbols(expression):
            holders = used.setdefault(symbol, [])
            if pkg.display not in holders:
                holders.append(pkg.display)

    licenses = tuple(
        License(
            license_id=lid,
            name=ref_name.get(lid, lid),
            text=ref_text.get(lid, ""),
            used_by=tuple(holders),
        )
        for lid, holders in sorted(used.items())
    )
    return doc.model_copy(update={"licenses": licenses})
