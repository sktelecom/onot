# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Grouping for the warnings the CLI reports.

A large SBOM can produce hundreds of lines, one per component, which scrolls the useful part
of the run off the screen. The lines still print, but a count by kind goes last so the shape of
the problem is visible without reading all of them.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable

# Ordered: the first pattern that matches decides the kind.
_KINDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("components without license information", re.compile(r"^no license information for ")),
    ("licenses without bundled text", re.compile(r"^missing license text for ")),
    ("unparseable license expressions", re.compile(r"^unparseable expression for ")),
)
_OTHER = "other"


def classify(warning: str) -> str:
    for label, pattern in _KINDS:
        if pattern.match(warning):
            return label
    return _OTHER


def summarize(warnings: Iterable[str]) -> str:
    """One line naming the total and the breakdown, or "" when there is nothing to report."""
    counts = Counter(classify(warning) for warning in warnings)
    total = sum(counts.values())
    if total == 0:
        return ""
    order = [label for label, _ in _KINDS] + [_OTHER]
    parts = [f"{counts[label]} {label}" for label in order if counts[label]]
    noun = "warning" if total == 1 else "warnings"
    return f"{total} {noun} ({', '.join(parts)})"
