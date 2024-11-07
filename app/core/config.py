from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, PostgresDsn, RedisDsn
from pydantic_core import MultiHostUrl, Url
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthConfig(BaseModel):
    CLIENT_ID: str
    SECRET_KEY: str
    REDIRECT_URI: str


class DataBaseConfig(BaseModel):
    DB: str = Field(serialization_alias="path")
    HOST: str = Field(serialization_alias="host")
    PORT: int = Field(serialization_alias="port")
    USER: str = Field(default="", serialization_alias="username")
    PASSWORD: str = Field(default="", serialization_alias="password")


class JWT(BaseModel):
    ALGORITHM: str = Field(default="ES384")
    ACCESS_TOKEN_EXPIRE_TIME: int = Field(default=60 * 60)
    REFRESH_TOKEN_EXPIRE_TIME: int = Field(default=60 * 60 * 24 * 7)


class AWS(BaseModel):
    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
    STORAGE_BUCKET_NAME: str
    S3_REGION_NAME: str


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    SECRET_KEY: str = Field(default="YtGHVqSAzFyaHk2OV5XQg3")
    BASE_URL: str = Field(default="http://localhost:8000")

    CORS_ALLOWED_ORIGINS: List[str] = Field(default_factory=list, frozen=True)
    ALLOWED_HOSTS: List[str] = Field(default_factory=list, frozen=True)

    PROJECT_NAME: str = Field(default="API")
    API_URL: str = Field(default="/api")
    SWAGGER_URL: str = Field(default="/api")

    AWS: AWS
    OAUTH_GOOGLE: OAuthConfig

    POSTGRES: DataBaseConfig
    REDIS: DataBaseConfig

    @property
    def POSTGRES_DSN(self) -> MultiHostUrl:
        return PostgresDsn.build(scheme="postgresql+psycopg", **self.POSTGRES.model_dump(by_alias=True))

    @property
    def REDIS_DSN(self) -> Url:
        return RedisDsn.build(scheme="redis", **self.REDIS.model_dump(by_alias=True))

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_nested_delimiter="__",
    )


settings = Settings()
