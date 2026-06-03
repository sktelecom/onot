# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""원격 라이선스 전문 조회(httpx + 지수 백오프 재시도 + 프록시 존중).

번들에 없는 신규/희귀 라이선스를 온라인에서 보충하는 보조 경로. 에어갭/오프라인에서는
호출하지 않는다. `trust_env=True`로 HTTP_PROXY/HTTPS_PROXY를 존중한다.
"""

from __future__ import annotations

import re
import time

import httpx

# SPDX license/exception id 문자셋. 이 외 문자(공백·개행·슬래시 등)는 절대 유효하지 않으므로
# URL 보간 전에 차단한다(InvalidURL 크래시·인젝션 방지).
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
