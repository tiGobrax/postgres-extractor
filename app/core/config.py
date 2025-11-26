import os
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


ENV_FILE = Path(".env")
DEFAULT_STORAGE_PATH = "./data"
DEFAULT_GCS_BUCKET = "gobrax-data-lake"
DEFAULT_GCS_BASE_PATH = "data-lake/postgres"
DEFAULT_GCS_CREDENTIALS_PATH = "postgres@gobrax-data.iam.gserviceaccount.com.json"
REQUIRED_ENV_VARS: Sequence[str] = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
)


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    STORAGE_PATH: str = DEFAULT_STORAGE_PATH
    GCP_BUCKET_NAME: str = DEFAULT_GCS_BUCKET
    GCP_BASE_PATH: str = DEFAULT_GCS_BASE_PATH
    GCP_CREDENTIALS_PATH: str = DEFAULT_GCS_CREDENTIALS_PATH

    class Config:
        env_file = None  # load order handled manually


_settings: Settings | None = None


def _load_environment() -> None:
    """
    Ensure we prefer .env locally and fall back to env vars (e.g. GitHub Secrets).

    The explicit load keeps local development predictable and avoids relying
    on CI/CD runners having a copy of the .env file.
    """

    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        return

    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        missing_vars = ", ".join(missing)
        raise RuntimeError(
            "Missing configuration. Provide a .env file or define the following "
            f"environment variables (e.g. via GitHub Secrets): {missing_vars}"
        )


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _load_environment()
        _settings = Settings()
        # force storage path to the default regardless of env vars
        _settings.STORAGE_PATH = DEFAULT_STORAGE_PATH
        # ensure storage path exists
        Path(_settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    return _settings
