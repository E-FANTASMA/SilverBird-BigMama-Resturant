from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Project X API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/project_x"
    )

    jwt_secret_key: str = "change-me"
    jwt_refresh_secret_key: str = "change-me-too"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    paystack_secret_key: str = "paystack-secret"
    paystack_public_key: str = "paystack-public"
    paystack_base_url: str = "https://api.paystack.co"
    paystack_webhook_secret: str = "paystack-webhook-secret"

    supabase_url: str = "https://example.supabase.co"
    supabase_service_role_key: str = "supabase-service-role-key"
    supabase_bucket_name: str = "food-images"

    restaurant_name: str = "Big Mama Restaurant"
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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
