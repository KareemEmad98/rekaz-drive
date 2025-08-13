import pathlib
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = pathlib.Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    app_name: str = "Rakez Drive"
    environment: str = "dev"

    auth_bearer_token: str

    storage: str = "fs"

    fs_base_path: str = "./storage"

    database_url: str = "sqlite:///./metadata.db"

    s3_endpoint: str = ""
    s3_region: str = "us-north-1"
    s3_bucket: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_session_token: str = ""
    s3_force_path_style: bool = False

    ftp_host: str = "ftp.drivehq.com"
    ftp_port: int = 21
    ftp_user: str = ""
    ftp_password: str = ""
    ftp_tls: bool = True
    ftp_base_dir: str = "/"
    ftp_timeout: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
