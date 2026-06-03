# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""API 라우트: healthz, formats, parse, render.

업로드는 메모리에서 임시파일로 받아 처리 후 폐기(stateless). 경로는 사용자 입력에서
받지 않는다. 업로드 크기를 제한한다.
"""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from onot.core.config import CompanyConfig, Settings
from onot.core.naming import output_filename
from onot.domain.errors import IngestError, LicenseError, OnotError
from onot.ingest import available_formats as _input_formats
from onot.ingest import load_document
from onot.ingest.base import IngestResult
from onot.license.resolver import LicenseResolver
from onot.rendering import available_formats, get_renderer, render
from onot.rendering.registry import is_supported

router = APIRouter()

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
_LANGS = ("ko", "en")
_MEDIA_TYPES = {
    "html": "text/html; charset=utf-8",
    "text": "text/plain; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "markdown": "text/markdown; charset=utf-8",
    "md": "text/markdown; charset=utf-8",
    "pdf": "application/pdf",
}


async def _read_upload(file: UploadFile) -> tuple[bytes, str]:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="uploaded file too large")
    if not data:
        raise HTTPException(status_code=400, detail="empty upload")
    suffix = Path(file.filename or "").suffix  # 디렉터리 성분 없이 확장자만(traversal 방지)
    return data, suffix


def _parse_bytes(data: bytes, suffix: str) -> IngestResult:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        return load_document(path)
    finally:
        Path(path).unlink(missing_ok=True)


def _http_error(err: OnotError) -> HTTPException:
    if isinstance(err, IngestError):
        return HTTPException(status_code=400, detail=str(err))
    if isinstance(err, LicenseError):
        return HTTPException(status_code=422, detail=str(err))
    return HTTPException(status_code=500, detail=str(err))


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/api/formats")
def formats() -> dict:
    return {"output": list(available_formats()), "input": list(_input_formats())}


@router.post("/api/parse")
async def parse(file: UploadFile = File(...)) -> dict:
    data, suffix = await _read_upload(file)
    try:
        ingest_result = _parse_bytes(data, suffix)
        resolved = LicenseResolver().resolve(ingest_result.document)
    except OnotError as err:
        raise _http_error(err) from err
    return {
        "document": resolved.document.model_dump(mode="json"),
        "warnings": [*ingest_result.warnings, *resolved.warnings],
    }


@router.post("/api/render")
async def render_notice(
    file: UploadFile = File(...),
    format: str = Form("html"),  # noqa: A002
    lang: str = Form("en"),
    download: bool = Form(False),
    organization: str = Form(""),
    contact_email: str = Form(""),
    copyright_holder: str = Form(""),
    source_download_url: str = Form(""),
) -> Response:
    if not is_supported(format):
        raise HTTPException(status_code=400, detail=f"unknown output format: {format}")
    if lang not in _LANGS:
        raise HTTPException(status_code=400, detail=f"unsupported lang: {lang}")

    data, suffix = await _read_upload(file)
    settings = Settings(
        default_lang=lang,
        company=CompanyConfig(
            organization=organization,
            contact_email=contact_email,
            copyright_holder=copyright_holder,
            source_download_url=source_download_url,
        ),
    )
    try:
        ingest_result = _parse_bytes(data, suffix)
        resolved = LicenseResolver(offline=settings.offline).resolve(ingest_result.document)
    except OnotError as err:
        raise _http_error(err) from err

    now = datetime.now()
    content = render(resolved.document, format, settings=settings, now=now)
    headers = {}
    if download:
        ext = get_renderer(format, settings=settings).file_extension
        filename = output_filename(resolved.document.name, ext, now)
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return Response(content=content, media_type=_MEDIA_TYPES.get(format), headers=headers)
