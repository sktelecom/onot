# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Jinja custom filters: anchor slugs, token linkification of license expressions."""

from __future__ import annotations

import re
from collections.abc import Iterable

from markupsafe import Markup, escape

from onot.core.naming import slugify

# SPDX expression tokens: id (alphanumeric/./-/+), parentheses, whitespace, any single char otherwise
_TOKEN = re.compile(r"[A-Za-z0-9.+-]+|\(|\)|\s+|.")


def anchor(license_id: str) -> str:
    return slugify(license_id)


def license_links(expression: str, known_ids: Iterable[str]) -> Markup:
    """Tokenize the expression and wrap only known license ids in internal anchor links (no substring collisions)."""
    known = set(known_ids)
    parts: list[str] = []
    for token in _TOKEN.findall(expression):
        if token in known:
            parts.append(f'<a href="#{escape(slugify(token))}">{escape(token)}</a>')
        else:
            parts.append(str(escape(token)))
    return Markup("".join(parts))


def md_cell(value: object) -> str:
    """Escape untrusted SBOM/user text for a Markdown table cell.

    Package names/versions come from third-party components, so pipes and newlines would break
    the table and link syntax could inject active links. Escapes the structural characters.
    """
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("\r\n", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def md_inline(value: object) -> str:
    """Neutralize Markdown link syntax and newlines for untrusted values used inline (not a table cell)."""
    return (
        str(value)
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("\r\n", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def oneline(value: object) -> str:
    """Flatten newlines so an untrusted value cannot forge structural lines in plain-text output."""
    return str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def md_code_block(text: str) -> str:
    """Wrap in a Markdown code fence. Uses a fence longer than any backtick run in the body to prevent fence escaping."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"
