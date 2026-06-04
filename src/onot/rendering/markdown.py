# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""MarkdownRenderer — GitHub-flavored Markdown notice."""

from __future__ import annotations

from onot.rendering.base import TemplateRenderer


class MarkdownRenderer(TemplateRenderer):
    format_id = "markdown"
    file_extension = "md"
    template_name = "markdown/notice.md.jinja"
    autoescape: list[str] = []
