#!/usr/bin/env python3
# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Fail if CHANGELOG.md has no section for the current pyproject version.

Guards against shipping a release whose notes were never written (regression guard for D5).
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    changelog = (ROOT / "CHANGELOG.md").read_text()
    if re.search(rf"^## \[{re.escape(version)}\]", changelog, re.MULTILINE):
        print(f"OK: CHANGELOG has an entry for {version}.")
        return 0
    print(
        f"CHANGELOG.md is missing a '## [{version}]' section for the current version.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
