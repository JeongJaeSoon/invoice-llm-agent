from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    debug: bool = False
    environment: Literal["development", "production"] = "development"
    log_level: str = "INFO"

    # API 설정
    api_version: str = "v1"
    api_prefix: str = "/api/v1"

    # OpenAI 설정
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    openai_max_tokens: int = 4000

    # Internal API 설정
    internal_api_url: str
    internal_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


settings = Settings()
