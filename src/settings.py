from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    SERVER: str | None
    DATABASE: str | None
    DB_USER: str | None
    PASSWORD: str | None
    PORT: str | None
    SECRET_KEY: str | None
    LOG_LEVEL: str
    RELOAD: bool
    ALGORITHM: str | None
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    KEY_PEM: str | None
    ASTRA_TOKEN: str | None
    ASTRA_ENDPOINT: str | None
    ASTRA_CLIENTE_ID: str | None
    CERT_PEM: str | None


SETTINGS = Settings()  # type: ignore
