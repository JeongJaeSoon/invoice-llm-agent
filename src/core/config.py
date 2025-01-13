from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class ValidationError(Exception):
    """설정 검증 에러"""

    pass


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    debug: bool = False
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"

    # API 설정
    api_version: str = "v1"
    api_prefix: str = "/api/v1"

    # OpenAI 설정
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo"
    openai_max_tokens: int = 4000

    # Internal API 설정
    internal_api_url: Optional[str] = None
    internal_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="APP_",
    )

    def validate_required_settings(self) -> None:
        """필수 환경 변수 검증"""
        if self.environment != "test":
            missing_fields = []
            if not self.openai_api_key:
                missing_fields.append("OPENAI_API_KEY")
            if not self.internal_api_url:
                missing_fields.append("INTERNAL_API_URL")
            if not self.internal_api_key:
                missing_fields.append("INTERNAL_API_KEY")

            if missing_fields:
                fields = ", ".join(missing_fields)
                error_msg = f"Missing required environment variables: {fields}"
                raise ValidationError(error_msg)


settings = Settings()

try:
    settings.validate_required_settings()
except ValidationError:
    if settings.environment != "test":
        raise
