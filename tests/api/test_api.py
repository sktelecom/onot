"""API 계약: healthz, formats, parse, render(포맷·언어·다운로드·회사)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures" / "sbom"
SAMPLE = ROOT / "sample" / "SPDXRdfExample-v2.3.xlsx"


def upload(path) -> dict:
    path = Path(path)
    return {"file": (path.name, path.read_bytes())}


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_formats(client):
    body = client.get("/api/formats").json()
    assert "html" in body["output"]
    assert "pdf" in body["output"]
    assert set(body["input"]) == {"spdx", "cyclonedx", "excel"}


@pytest.mark.parametrize("name", ["example.spdx.json", "example.cdx.json", "example.cdx.xml"])
def test_parse_formats(client, name):
    resp = client.post("/api/parse", files=upload(FIX / name))
    assert resp.status_code == 200
    body = resp.json()
    assert body["document"]["packages"]
    assert body["document"]["name"]


def test_parse_excel(client):
    resp = client.post("/api/parse", files=upload(SAMPLE))
    assert resp.status_code == 200
    assert resp.json()["document"]["packages"]


def test_render_html(client):
    resp = client.post(
        "/api/render", files=upload(FIX / "example.spdx.json"), data={"format": "html"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "OSS Notice for example-product" in resp.text


@pytest.mark.parametrize(("fmt", "ctype"), [("text", "text/plain"), ("markdown", "text/markdown")])
def test_render_text_markdown(client, fmt, ctype):
    resp = client.post("/api/render", files=upload(FIX / "example.spdx.json"), data={"format": fmt})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(ctype)


def test_render_download_disposition(client):
    resp = client.post(
        "/api/render",
        files=upload(FIX / "example.spdx.json"),
        data={"format": "html", "download": "true"},
    )
    cd = resp.headers["content-disposition"]
    assert "attachment; filename=" in cd
    assert ".html" in cd


def test_render_lang_ko(client):
    resp = client.post(
        "/api/render",
        files=upload(FIX / "example.spdx.json"),
        data={"format": "html", "lang": "ko"},
    )
    assert "오픈소스 고지" in resp.text


def test_render_company_injected(client):
    resp = client.post(
        "/api/render",
        files=upload(FIX / "example.spdx.json"),
        data={"format": "html", "organization": "SKT", "contact_email": "oss@skt.example"},
    )
    assert "oss@skt.example" in resp.text


def test_render_unknown_format_400(client):
    resp = client.post(
        "/api/render", files=upload(FIX / "example.spdx.json"), data={"format": "xml"}
    )
    assert resp.status_code == 400


def test_render_invalid_lang_400(client):
    resp = client.post(
        "/api/render",
        files=upload(FIX / "example.spdx.json"),
        data={"format": "html", "lang": "xx"},
    )
    assert resp.status_code == 400


def test_render_pdf_when_available(client):
    pytest.importorskip("weasyprint")
    resp = client.post(
        "/api/render",
        files=upload(FIX / "example.spdx.json"),
        data={"format": "pdf", "download": "true"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"
    assert ".pdf" in resp.headers["content-disposition"]
