from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    sentry_dsn: Optional[str] = None
    debug: bool = False
    allowed_hosts: list[str] = []
    csrf_trusted_origins: list[str] = []
    secret_key: str
    database_url: str = "postgres:///perf_ink"
    celery_broker_url: str = "redis://"


config = Config(_env_file=".env", _env_file_encoding="utf-8")
