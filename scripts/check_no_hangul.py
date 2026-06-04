# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""Guard: fail if any tracked text file contains Hangul (Korean) characters.

onot is an English-only project so it stays accessible to a global audience;
this check keeps Korean from creeping back into code, comments, or docs.

Usage: python scripts/check_no_hangul.py
"""

from __future__ import annotations

import re
import subprocess
import sys

# Hangul syllables (AC00-D7A3), the Hangul Jamo block (1100-11FF),
# and compatibility Jamo (3130-318F). Built from code points with chr()
# so this guard's own source contains no Hangul to match.
_RANGES = ((0xAC00, 0xD7A3), (0x1100, 0x11FF), (0x3130, 0x318F))
HANGUL = re.compile("[" + "".join(f"{chr(lo)}-{chr(hi)}" for lo, hi in _RANGES) + "]")


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    )
    offenders = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = raw.decode("utf-8", "surrogateescape")
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue  # binary or unreadable file -> skip
        if HANGUL.search(text):
            offenders.append(path)

    if offenders:
        print("ERROR: Hangul characters found in tracked files:", file=sys.stderr)
        for path in offenders:
            print(f"  - {path}", file=sys.stderr)
        print(
            "\nonot is English-only. Please translate the listed content to English.",
            file=sys.stderr,
        )
        return 1

    print("OK: no Hangul in tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
