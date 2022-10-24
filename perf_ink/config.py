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

    email_host: str = ""
    email_host_password: str = ""
    email_host_user: str = ""

    account_email_verification: str = "none"

    default_from_email: str = ""
    server_email: str = ""


config = Config(_env_file=".env", _env_file_encoding="utf-8")
