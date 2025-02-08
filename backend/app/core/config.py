from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "NHL Fantasy Optimizer"
    DATABASE_URL: str
    REDIS_URL: str | None = None

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()