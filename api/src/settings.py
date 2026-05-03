from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_uri: str
    log_file: str = "app.log"
    echo_sql: bool = True

    model_config = SettingsConfigDict(
        env_file="server/src/.env",
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
