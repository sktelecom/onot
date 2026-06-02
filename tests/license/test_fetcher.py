"""원격 fetcher: 성공/예외필드/404/재시도(respx mock, 네트워크 없음)."""

from __future__ import annotations

import httpx
import respx

from onot.license.fetcher import RemoteLicenseFetcher

URL = "https://spdx.org/licenses"


@respx.mock
def test_fetch_success():
    respx.get(f"{URL}/MIT.json").mock(
        return_value=httpx.Response(200, json={"licenseText": "MIT TEXT"})
    )
    fetcher = RemoteLicenseFetcher(backoff=0)
    assert fetcher.fetch_text("MIT") == "MIT TEXT"
    fetcher.close()


@respx.mock
def test_fetch_exception_field():
    respx.get(f"{URL}/Classpath-exception-2.0.json").mock(
        return_value=httpx.Response(200, json={"licenseExceptionText": "EXC"})
    )
    fetcher = RemoteLicenseFetcher(backoff=0)
    assert fetcher.fetch_text("Classpath-exception-2.0", is_exception=True) == "EXC"


@respx.mock
def test_fetch_404_returns_none():
    respx.get(f"{URL}/Nope.json").mock(return_value=httpx.Response(404))
    fetcher = RemoteLicenseFetcher(backoff=0)
    assert fetcher.fetch_text("Nope") is None


@respx.mock
def test_fetch_retries_then_succeeds():
    route = respx.get(f"{URL}/MIT.json").mock(
        side_effect=[httpx.ConnectError("boom"), httpx.Response(200, json={"licenseText": "OK"})]
    )
    fetcher = RemoteLicenseFetcher(retries=3, backoff=0)
    assert fetcher.fetch_text("MIT") == "OK"
    assert route.call_count == 2


@respx.mock
def test_fetch_exhausts_retries_returns_none():
    respx.get(f"{URL}/MIT.json").mock(side_effect=httpx.ConnectError("down"))
    fetcher = RemoteLicenseFetcher(retries=2, backoff=0)
    assert fetcher.fetch_text("MIT") is None


def test_invalid_id_returns_none_without_network():
    # SPDX id 문자셋 밖(공백/개행/슬래시)은 URL 보간 전에 차단 → 네트워크 호출 없음
    fetcher = RemoteLicenseFetcher(retries=1, backoff=0)
    assert fetcher.fetch_text("foo bar\nbaz") is None
    assert fetcher.fetch_text("../etc/passwd") is None
    fetcher.close()
