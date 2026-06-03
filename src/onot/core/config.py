# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""설정. 회사 정보·언어·테마·오프라인 모드. 우선순위: CLI/명시 인자 > yaml > 환경변수 > 기본값.

환경변수 예: ONOT_DEFAULT_LANG=ko, ONOT_COMPANY__ORGANIZATION="SK telecom".
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from onot.domain.errors import ConfigError

Lang = Literal["ko", "en"]


class CompanyConfig(BaseModel):
    organization: str = ""
    contact_email: str = ""
    copyright_holder: str = ""
    copyright_year: int | None = None
    source_download_url: str = ""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ONOT_", env_nested_delimiter="__")

    default_lang: Lang = "en"
    theme: str = "default"
    offline: bool = True
    company: CompanyConfig = CompanyConfig()


def load_settings(
    config_path: str | Path | None = None,
    *,
    lang: str | None = None,
    offline: bool | None = None,
) -> Settings:
    """yaml 설정 + 환경변수 + CLI 오버라이드를 병합한 Settings를 만든다.

    CLI 인자는 yaml 위에 병합되며, 잘못된 값(예: 미지원 lang)은 ConfigError로 보고한다.
    """
    data: dict = {}
    if config_path is not None:
        loaded = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
        if loaded:
            data = loaded
    if lang is not None:
        data["default_lang"] = lang
    if offline is not None:
        data["offline"] = offline
    try:
        return Settings(**data)
    except ValidationError as exc:
        raise ConfigError(f"invalid configuration: {exc}") from exc
