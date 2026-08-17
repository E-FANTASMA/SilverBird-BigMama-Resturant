from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Silverbird BigMama Restaurant"
    api_title: str = "Silverbird BigMama Restaurant API"
    api_description: str = "Backend API for the Silverbird BigMama Restaurant food ordering system."
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    auto_run_migrations_on_startup: bool = True
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://silver-bird-big-mama-resturant.vercel.app",
        ]
    )

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/silverbird_bigmama_restaurant"
    )

    jwt_secret_key: str = "change-me"
    jwt_refresh_secret_key: str = "change-me-too"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 30

    paystack_secret_key: str = "paystack-secret"
    paystack_public_key: str = "paystack-public"
    paystack_base_url: str = "https://api.paystack.co"
    paystack_webhook_secret: str = "paystack-webhook-secret"

    supabase_url: str = "https://example.supabase.co"
    supabase_service_role_key: str = "supabase-service-role-key"
    supabase_bucket_name: str = "food-images"

    restaurant_name: str = "Silverbird BigMama Restaurant"
    restaurant_latitude: float = 6.4350
    restaurant_longitude: float = 3.4219
    delivery_base_fee: float = 1000.0
    delivery_fee_per_km: float = 350.0
    max_upload_size_bytes: int = 5 * 1024 * 1024

    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = "noreply@example.com"
    smtp_password: str = "secret"
    sms_provider_api_key: str = "sms-key"

    initial_admin_first_name: str | None = None
    initial_admin_last_name: str | None = None
    initial_admin_email: str | None = None
    initial_admin_phone: str | None = None
    initial_admin_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_value(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "no"}:
                return False
            if normalized in {"development", "dev", "true", "1", "yes"}:
                return True
        return value

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
