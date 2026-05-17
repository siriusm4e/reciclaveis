"""Settings — carregadas de variáveis de ambiente / .env via Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- App -----
    APP_NAME: str = "PNR"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    TZ: str = "America/Sao_Paulo"

    # ----- Database -----
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # ----- Redis -----
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    JWT_BLOCKLIST_REDIS_URL: str = "redis://redis:6379/3"
    WS_PUBSUB_REDIS_URL: str = "redis://redis:6379/4"

    # ----- Auth / JWT -----
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_TTL_MINUTES: int = 15
    JWT_REFRESH_TOKEN_TTL_DAYS: int = 7
    JWT_ISSUER: str = "pnr-api"

    # ----- Argon2id (OWASP 2024) -----
    ARGON2_MEMORY_COST: int = 19456  # KiB
    ARGON2_TIME_COST: int = 2
    ARGON2_PARALLELISM: int = 1

    # ----- MFA -----
    MFA_ISSUER: str = "PNR"
    MFA_LOGIN_LOCK_THRESHOLD: int = 5

    # ----- CORS -----
    CORS_ALLOWED_ORIGINS: str = "http://localhost,http://localhost:5173"

    # ----- Uploads -----
    UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024
    UPLOAD_ALLOWED_MIME: str = "image/jpeg,image/png,image/webp,application/pdf"
    STORAGE_BASE_PATH: str = "/app/storage"
    STORAGE_PUBLIC_URL: str = "/storage"

    # ----- Geolocalização -----
    GEO_OFFSET_URBANO_M: int = 250
    GEO_OFFSET_RURAL_M: int = 1500
    GEO_DEFAULT_SRID: int = 4326

    # ----- Receita Federal -----
    RECEITA_PROVIDER: Literal["stub", "hubdev", "serpro"] = "stub"
    RECEITA_API_TOKEN: str = ""

    # ----- Push -----
    FCM_CREDENTIALS_JSON_BASE64: str = ""
    FCM_PROJECT_ID: str = ""

    # ----- Alerta Pago / Créditos -----
    ALERTA_PAGO_COBERTURA_MINIMA: int = 3
    CREDITOS_EXPIRAM: bool = False

    # ----- Oportunidades públicas -----
    OPORTUNIDADE_PUBLICA_PRAZO_MIN_DIAS_UTEIS: int = 5

    # ----- LGPD -----
    LGPD_GRACA_EXCLUSAO_DIAS: int = 30
    AUDIT_LOG_RETENCAO_ANOS: int = 5

    # ----- Observabilidade -----
    METRICS_TOKEN: str = "change_me"
    OTEL_SERVICE_NAME: str = "pnr-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://jaeger:4318"
    OTEL_TRACES_SAMPLER: str = "parentbased_traceidratio"
    OTEL_TRACES_SAMPLER_ARG: float = 0.1

    # ----- Rate limit -----
    RATE_LIMIT_PUBLIC: str = "100/minute"
    RATE_LIMIT_AUTHENTICATED: str = "1000/minute"

    # ----- Superadmin seed -----
    SUPERADMIN_EMAIL: str = "admin@pnr.com.br"
    SUPERADMIN_PASSWORD: str = "change_me_on_first_login"
    SUPERADMIN_CPF: str = "00000000000"

    @field_validator("CORS_ALLOWED_ORIGINS")
    @classmethod
    def _no_wildcard_in_prod(cls, v: str, info) -> str:
        env = (info.data.get("APP_ENV") or "").lower()
        if env == "production" and "*" in v:
            raise ValueError("CORS_ALLOWED_ORIGINS não pode conter '*' em produção")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def upload_allowed_mime_set(self) -> set[str]:
        return {m.strip() for m in self.UPLOAD_ALLOWED_MIME.split(",") if m.strip()}

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
