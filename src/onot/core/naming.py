# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Output file naming rules. (HTML anchor slugs are added in M4 license_links)"""

from __future__ import annotations

import re
from datetime import datetime

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def slugify(name: str) -> str:
    return _UNSAFE.sub("_", name.strip()).strip("_") or "OSS_Notice"


def output_filename(product: str, ext: str, now: datetime) -> str:
    """OSS_Notice_<Product>_<YYYYmmdd_HHMMSS>.<ext>"""
    return f"OSS_Notice_{slugify(product)}_{now:%Y%m%d_%H%M%S}.{ext}"
