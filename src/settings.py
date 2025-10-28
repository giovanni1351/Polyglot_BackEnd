from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    SERVER: str | None = None
    DATABASE: str | None = None
    DB_USER: str | None = None
    PASSWORD: str | None = None
    PORT: str | None = None
    SECRET_KEY: str | None = None
    LOG_LEVEL: str = "INFO"
    RELOAD: bool = False
    ALGORITHM: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    KEY_PEM: str | None = None
    ASTRA_TOKEN: str | None = None
    ASTRA_ENDPOINT: str | None = None
    ASTRA_CLIENTE_ID: str | None = None
    CERT_PEM: str | None = None


SETTINGS = Settings()  # type: ignore
