from pathlib import Path
from typing import Annotated, List

from pydantic import BaseModel, Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataBaseConfig(BaseModel):
    db: Annotated[str, Field(serialization_alias="path")]
    host: Annotated[str, Field(serialization_alias="host")]
    port: Annotated[int, Field(serialization_alias="port")]
    user: Annotated[str, Field(default="", serialization_alias="username")]
    password: Annotated[str, Field(default="", serialization_alias="password")]


class JWT(BaseModel):
    algorithm: Annotated[str, Field(default="ES384")]
    access_token_expire_time: Annotated[int, Field(default=3600)]
    refresh_token_expire_time: Annotated[int, Field(default=604800)]


class OAuthConfig(BaseModel):
    client_id: str
    secret_key: str
    redirect_uri: str


class AWS(BaseModel):
    access_key_id: str
    secret_access_key: str
    storage_bucket_name: str
    s3_region_name: str


class ApiAdapter(BaseModel):
    key: str


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent.parent

    debug: Annotated[bool, Field(default=False)]
    base_url: Annotated[str, Field(default="http://localhost:8000")]
    secret_key: Annotated[str, Field(default="YtGHVqSAzFyaHk2OV5XQg3")]

    cors_allow_origin: List[str] = Field(default_factory=list, frozen=True)
    allowed_hosts: List[str] = Field(default_factory=list, frozen=True)

    project_name: Annotated[str, Field(default="API")]
    api_url: Annotated[str, Field(default="/api")]
    swagger_url: Annotated[str, Field(default="/api")]

    jwt: Annotated[JWT, Field(default_factory=JWT)]
    postgres: DataBaseConfig
    redis: DataBaseConfig

    aws: AWS
    oauth_google: OAuthConfig

    open_fiscal_data_api: ApiAdapter

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(scheme="postgresql+psycopg", **self.postgres.model_dump(by_alias=True))

    @property
    def redis_dsn(self) -> RedisDsn:
        return RedisDsn.build(scheme="redis", **self.redis.model_dump(by_alias=True))

    model_config = SettingsConfigDict(
        env_file=str(base_dir / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
        env_nested_delimiter="__",
    )


settings = Settings()
