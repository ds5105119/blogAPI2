from webtool.auth import JWTBackend, RedisJWTService

from app.core.config import settings
from app.dependencies.db import Redis

jwt_service = RedisJWTService(
    Redis,
    secret_key=settings.secret_key,
    access_token_expire_time=settings.jwt.access_token_expire_time,
    refresh_token_expire_time=settings.jwt.refresh_token_expire_time,
)

jwt_backend = JWTBackend(jwt_service)
