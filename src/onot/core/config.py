# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Settings: company info, language, theme, offline mode. Precedence: CLI/explicit args > yaml > env vars > defaults.

Env var example: ONOT_DEFAULT_LANG=en, ONOT_COMPANY__ORGANIZATION="Acme Inc".
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from onot.domain.errors import ConfigError

Lang = Literal["en"]


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
    """Build Settings by merging yaml config + env vars + CLI overrides.

    CLI args are merged on top of yaml; invalid values (e.g. an unsupported lang) are reported as ConfigError.
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
