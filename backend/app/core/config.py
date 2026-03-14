from pydantic import Field
from pydantic import computed_field, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # db
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    # token
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"  # temp
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # temp
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # temp
    # mails
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DEBUG: bool = True
    FRONTEND_URLS: list[str] = Field(description="allow frontend end points")
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

    @computed_field(return_type=str)
    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@localhost:5432/{self.POSTGRES_DB}"
        # docker-compose -> db

    @computed_field(return_type=str)
    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


setting = Settings()
