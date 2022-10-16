from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    database_name: str = "perf_ink"
    database_host: Optional[str] = None
    database_port: Optional[str] = None
    database_user: Optional[str] = None
    database_password: Optional[str] = None

    celery_broker_url: str = "redis://"


config = Config(_env_file='.env', _env_file_encoding='utf-8')
