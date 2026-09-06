# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Shared fixtures."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from onot import __version__

# The notice footer records the tool version. Golden files store this placeholder instead, so a
# release bump does not force every golden file to be rewritten.
VERSION_PLACEHOLDER = "0.0.0-test"


@pytest.fixture
def normalize_version() -> Callable[[str], str]:
    """Replace the running tool version with the placeholder the golden files use."""

    def normalize(text: str) -> str:
        return text.replace(__version__, VERSION_PLACEHOLDER)

    return normalize
