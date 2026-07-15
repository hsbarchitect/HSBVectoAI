"""
HSBVectoAI Backend — Configuration
All secrets loaded from environment variables / .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "HSBVectoAI Backend"
    debug: bool = False
    secret_key: str  # JWT signing secret — REQUIRED

    # Database
    database_url: str  # postgresql+asyncpg://user:pass@host/db — REQUIRED

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # AI
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_starter_monthly: str = ""
    stripe_price_pro_monthly: str = ""
    stripe_price_studio_monthly: str = ""
    stripe_price_starter_yearly: str = ""
    stripe_price_pro_yearly: str = ""
    stripe_price_studio_yearly: str = ""

    # CORS — comma separated origins
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # Plan limits
    starter_monthly_limit: int = 500  # messages/month
    pro_monthly_limit: int = -1       # unlimited
    studio_monthly_limit: int = -1    # unlimited

    # Device limits per plan
    starter_device_limit: int = 1
    pro_device_limit: int = 3
    studio_device_limit: int = 10

    def get_monthly_limit(self, plan: str) -> int:
        limits = {
            "starter": self.starter_monthly_limit,
            "pro": self.pro_monthly_limit,
            "studio": self.studio_monthly_limit,
        }
        return limits.get(plan, 0)

    def get_device_limit(self, plan: str) -> int:
        limits = {
            "starter": self.starter_device_limit,
            "pro": self.pro_device_limit,
            "studio": self.studio_device_limit,
        }
        return limits.get(plan, 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
