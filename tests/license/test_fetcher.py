# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Remote fetcher: success/exception field/404/retry (respx mock, no network)."""

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
    # Characters outside the SPDX id set (space/newline/slash) are blocked before URL interpolation -> no network call
    fetcher = RemoteLicenseFetcher(retries=1, backoff=0)
    assert fetcher.fetch_text("foo bar\nbaz") is None
    assert fetcher.fetch_text("../etc/passwd") is None
    fetcher.close()
