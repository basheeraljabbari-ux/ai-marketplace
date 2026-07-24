from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "AI Marketplace API"
    ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_marketplace"

    # Redis (queue + cache)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Storage (S3-compatible)
    STORAGE_BUCKET: str = "ai-marketplace-images"
    STORAGE_ENDPOINT_URL: str | None = None  # endpoint الـ API للرفع (خاص، مو قابل للتصفح عام)
    # الرابط العام للقراءة. R2 buckets خاصة افتراضياً و STORAGE_ENDPOINT_URL ما يخدم
    # الملفات للعامة — لازم رابط public/custom domain منفصل، وإلا أي جهة خارجية
    # (مثلاً Claude vision وهي تجيب الصورة) ترجع 400.
    # صيغته بـ R2 بدون جزء الـ bucket لأنه أصلاً مربوط ببكت واحد.
    STORAGE_PUBLIC_URL: str | None = None
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""

    # AI Provider (pluggable — see modules/ai/interface.py)
    AI_PROVIDER: str = "mock"  # 'mock' | 'anthropic' | 'openai'
    AI_API_KEY: str = ""

    # Search
    SEARCH_PROVIDER: str = "postgres"  # 'postgres' | 'opensearch'


@lru_cache
def get_settings() -> Settings:
    return Settings()
