from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Pydantic pulls these automatically from the environment
    POSTGRES_USER: str
    POSTGRES_SERVER: str
    POSTGRES_PASSWORD: SecretStr  # Encapsulates secret to protect from logging
    POSTGRES_DB: str

    POOL_SIZE: int
    MAX_OVERFLOW: int

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DEBUG: bool


    # Configures behavior (e.g., looking for .env locally but falling back to system env)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
