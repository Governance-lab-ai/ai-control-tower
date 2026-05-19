from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    app_name: str = Field(default="AI Governance Control Tower", validation_alias="APP_NAME")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/aigov",
        validation_alias="DATABASE_URL",
    )

    auth_mode: str = Field(default="local_mock", validation_alias="AUTH_MODE")
    llm_provider: str = Field(default="mock", validation_alias="LLM_PROVIDER")
    safety_provider: str = Field(default="local", validation_alias="SAFETY_PROVIDER")
    secret_provider: str = Field(default="env", validation_alias="SECRET_PROVIDER")
    telemetry_provider: str = Field(default="console", validation_alias="TELEMETRY_PROVIDER")
    data_governance_provider: str = Field(default="local", validation_alias="DATA_GOVERNANCE_PROVIDER")

    max_input_chars: int = Field(default=12000, validation_alias="MAX_INPUT_CHARS")
    max_output_chars: int = Field(default=12000, validation_alias="MAX_OUTPUT_CHARS")
    max_retrieved_documents: int = Field(default=5, validation_alias="MAX_RETRIEVED_DOCUMENTS")
    request_timeout_seconds: int = Field(default=30, validation_alias="REQUEST_TIMEOUT_SECONDS")
    rate_limit_per_minute: int = Field(default=60, validation_alias="RATE_LIMIT_PER_MINUTE")

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        allowed = {"local", "azure-dev", "production"}
        if value not in allowed:
            raise ValueError(f"APP_ENV must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("auth_mode")
    @classmethod
    def validate_auth_mode(cls, value: str) -> str:
        allowed = {"local_mock", "entra"}
        if value not in allowed:
            raise ValueError(f"AUTH_MODE must be one of: {', '.join(sorted(allowed))}")
        return value

    def validate_runtime_safety(self) -> None:
        if self.app_env == "production" and self.auth_mode == "local_mock":
            raise ValueError("AUTH_MODE=local_mock is not allowed in production.")
        if self.app_env == "production" and "localhost" in self.database_url:
            raise ValueError("DATABASE_URL must not point to localhost in production.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime_safety()
    return settings
