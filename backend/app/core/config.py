from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600
    base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()