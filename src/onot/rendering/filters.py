# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Jinja 커스텀 필터: 앵커 슬러그, 라이선스 표현식의 토큰 링크화."""

from __future__ import annotations

import re
from collections.abc import Iterable

from markupsafe import Markup, escape

from onot.core.naming import slugify

# SPDX 표현식 토큰: id(영숫자/./-/+), 괄호, 공백, 그 외 1글자
_TOKEN = re.compile(r"[A-Za-z0-9.+-]+|\(|\)|\s+|.")


def anchor(license_id: str) -> str:
    return slugify(license_id)


def license_links(expression: str, known_ids: Iterable[str]) -> Markup:
    """표현식을 토큰화해 알려진 라이선스 id만 내부 앵커 링크로 감싼다(부분 문자열 충돌 없음)."""
    known = set(known_ids)
    parts: list[str] = []
    for token in _TOKEN.findall(expression):
        if token in known:
            parts.append(f'<a href="#{escape(slugify(token))}">{escape(token)}</a>')
        else:
            parts.append(str(escape(token)))
    return Markup("".join(parts))


def md_code_block(text: str) -> str:
    """Markdown 코드펜스로 감싼다. 본문의 백틱 런보다 긴 펜스를 써서 fence 탈출을 막는다."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"
