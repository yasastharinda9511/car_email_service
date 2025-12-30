from pydantic import  Field
from functools import lru_cache

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "my-service"
    environment: str = "dev"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    # Mail Server
    mail_server_host: str
    mail_server_port: int

    email: str
    email_app_password: str

    introspect_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader.
    Ensures config is loaded once and reused.
    """
    return Settings()
