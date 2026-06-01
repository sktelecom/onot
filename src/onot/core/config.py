"""설정. 회사 정보·언어·테마·오프라인 모드. 우선순위: 명시 인자 > 환경변수 > 기본값.

환경변수 예: ONOT_DEFAULT_LANG=ko, ONOT_COMPANY__ORGANIZATION="SK telecom".
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

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
