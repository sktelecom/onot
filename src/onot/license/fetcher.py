# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Remote license full-text fetch (httpx + exponential backoff retries + proxy-aware).

A supplementary path that fetches new/rare licenses not in the bundle from online. Not
called in air-gapped/offline mode. `trust_env=True` honors HTTP_PROXY/HTTPS_PROXY.
"""

from __future__ import annotations

import re
import time

import httpx

# SPDX license/exception id character set. Any other character (whitespace, newline, slash, etc.)
# is never valid, so block it before URL interpolation (prevents InvalidURL crashes/injection).
_VALID_ID = re.compile(r"[A-Za-z0-9.+-]+")


class RemoteLicenseFetcher:
    BASE = "https://spdx.org/licenses"

    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        retries: int = 3,
        backoff: float = 0.2,
    ) -> None:
        self._client = client or httpx.Client(follow_redirects=True, timeout=15, trust_env=True)
        self._owns_client = client is None
        self._retries = max(1, retries)
        self._backoff = backoff

    def fetch_text(self, license_id: str, *, is_exception: bool = False) -> str | None:
        if not _VALID_ID.fullmatch(license_id):
            return None
        url = f"{self.BASE}/{license_id}.json"
        field = "licenseExceptionText" if is_exception else "licenseText"
        for attempt in range(self._retries):
            try:
                resp = self._client.get(url)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json().get(field) or None
            except (httpx.HTTPError, httpx.InvalidURL):
                if attempt < self._retries - 1:
                    time.sleep(self._backoff * (2**attempt))
        return None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()
