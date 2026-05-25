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
    evaluation_provider: str = Field(default="local", validation_alias="EVALUATION_PROVIDER")
    safety_provider: str = Field(default="local", validation_alias="SAFETY_PROVIDER")
    secret_provider: str = Field(default="env", validation_alias="SECRET_PROVIDER")
    telemetry_provider: str = Field(default="console", validation_alias="TELEMETRY_PROVIDER")
    data_governance_provider: str = Field(default="local", validation_alias="DATA_GOVERNANCE_PROVIDER")
    enable_demo_seed: bool = Field(default=True, validation_alias="ENABLE_DEMO_SEED")
    ollama_base_url: str = Field(default="http://host.docker.internal:11434", validation_alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", validation_alias="OLLAMA_MODEL")
    ollama_evaluation_model: str = Field(default="llama3.1", validation_alias="OLLAMA_EVALUATION_MODEL")

    max_input_chars: int = Field(default=12000, validation_alias="MAX_INPUT_CHARS")
    max_output_chars: int = Field(default=12000, validation_alias="MAX_OUTPUT_CHARS")
    max_retrieved_documents: int = Field(default=5, validation_alias="MAX_RETRIEVED_DOCUMENTS")
    request_timeout_seconds: int = Field(default=30, validation_alias="REQUEST_TIMEOUT_SECONDS")
    rate_limit_per_minute: int = Field(default=60, validation_alias="RATE_LIMIT_PER_MINUTE")
    evaluation_threshold_low: int = Field(default=55, validation_alias="EVALUATION_THRESHOLD_LOW")
    evaluation_threshold_medium: int = Field(default=70, validation_alias="EVALUATION_THRESHOLD_MEDIUM")
    evaluation_threshold_high: int = Field(default=80, validation_alias="EVALUATION_THRESHOLD_HIGH")
    evaluation_threshold_critical: int = Field(default=90, validation_alias="EVALUATION_THRESHOLD_CRITICAL")

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

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        allowed = {"mock", "ollama", "azure_openai"}
        if value not in allowed:
            raise ValueError(f"LLM_PROVIDER must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("evaluation_provider")
    @classmethod
    def validate_evaluation_provider(cls, value: str) -> str:
        allowed = {"local", "semantic_local", "ollama_local"}
        if value not in allowed:
            raise ValueError(f"EVALUATION_PROVIDER must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("evaluation_threshold_low", "evaluation_threshold_medium", "evaluation_threshold_high", "evaluation_threshold_critical")
    @classmethod
    def validate_score_threshold(cls, value: int) -> int:
        if value < 0 or value > 100:
            raise ValueError("Evaluation thresholds must be between 0 and 100.")
        return value

    def validate_runtime_safety(self) -> None:
        if self.app_env == "production" and self.auth_mode == "local_mock":
            raise ValueError("AUTH_MODE=local_mock is not allowed in production.")
        if self.app_env == "production" and self.enable_demo_seed:
            raise ValueError("ENABLE_DEMO_SEED=true is not allowed in production.")
        if self.app_env == "production" and "localhost" in self.database_url:
            raise ValueError("DATABASE_URL must not point to localhost in production.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime_safety()
    return settings
