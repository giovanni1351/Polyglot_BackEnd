from pydantic_settings import BaseSettings, SettingsConfigDict
from pylogkit import get_logger


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    SERVER: str | None
    DATABASE: str | None
    USER: str | None
    PASSWORD: str | None
    PORT: str | None
    SECRET_KEY: str | None
    LOG_LEVEL: str
    RELOAD: bool
    ALGORITHM: str | None
    ACCESS_TOKEN_EXPIRE_MINUTES: int


LOGGER = get_logger("mylogger", level=Settings().LOG_LEVEL)
