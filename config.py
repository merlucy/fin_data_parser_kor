from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    dart_api_key: str
    database_url: str
    dart_daily_call_limit: int = 20000
    dart_request_delay_seconds: float = 0.4
    dart_cache_dir: Path = Path("./cache/dart")


settings = Settings()
