# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""API 보안/입력 검증: XXE 업로드, 미지원/빈/대용량, 파일명 traversal."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures" / "sbom"


def upload(path) -> dict:
    path = Path(path)
    return {"file": (path.name, path.read_bytes())}


@pytest.mark.parametrize("name", ["xxe.cdx.xml", "billion-laughs.cdx.xml"])
def test_malicious_xml_upload_rejected(client, name):
    resp = client.post("/api/parse", files=upload(FIX / name))
    assert resp.status_code == 400
    # 단순 파싱 실패가 아니라 XXE 가드에 의한 거부임을 명시 단언
    assert "XXE" in resp.json()["detail"] or "unsafe" in resp.json()["detail"].lower()


def test_render_path_rejects_malicious_xml(client):
    # render 엔드포인트도 동일 XXE 가드를 거친다
    resp = client.post("/api/render", files=upload(FIX / "xxe.cdx.xml"), data={"format": "html"})
    assert resp.status_code == 400


def test_http_error_mapping():
    from onot.api.routes import _http_error
    from onot.domain.errors import ConfigError, IngestError, LicenseError

    assert _http_error(IngestError("x")).status_code == 400
    assert _http_error(LicenseError("x")).status_code == 422
    assert _http_error(ConfigError("x")).status_code == 500


def test_unsupported_input_400(client):
    resp = client.post("/api/parse", files={"file": ("x.txt", b"not an sbom")})
    assert resp.status_code == 400


def test_empty_upload_400(client):
    resp = client.post("/api/parse", files={"file": ("x.json", b"")})
    assert resp.status_code == 400


def test_oversize_upload_413(client, monkeypatch):
    import onot.api.routes as routes

    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 10)
    resp = client.post("/api/parse", files={"file": ("big.json", b"0123456789ABCDEF")})
    assert resp.status_code == 413


def test_filename_path_is_ignored(client):
    # 업로드 파일명에 경로가 있어도 suffix만 사용(traversal 불가), 정상 파싱
    payload = (FIX / "example.spdx.json").read_bytes()
    resp = client.post("/api/parse", files={"file": ("../../../etc/passwd.json", payload)})
    assert resp.status_code == 200
    assert resp.json()["document"]["name"] == "example-product"
