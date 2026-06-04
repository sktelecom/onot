# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""TextRenderer — plain-text notice."""

from __future__ import annotations

from onot.rendering.base import TemplateRenderer


class TextRenderer(TemplateRenderer):
    format_id = "text"
    file_extension = "txt"
    template_name = "text/notice.txt.jinja"
    autoescape: list[str] = []
