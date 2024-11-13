from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigSetting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_USER: str
    DB_PASSWORD: str
    DB_HOSTNAME: str
    DB_PORT: int
    DB_NAME: str
    DOCS_ENDPOINT: str
    REDOCS_ENDPOINT: str
    DEBUG: bool
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_LIMIT: int = 30     # In Minutes
    REFRESH_TOKEN_EXPIRE_LIMIT: int = 2     # In Days
    BROKER_URL: str
    BROKER_BACKEND: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    BACKEND_DOMAIN: str


@lru_cache
def get_settings():
    return ConfigSetting()


settings = get_settings()
