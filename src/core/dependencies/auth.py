from webtool.auth import AnnoSessionBackend, JWTBackend, RedisJWTService

from .db import Redis, settings

jwt_service = RedisJWTService(
    Redis,
    secret_key=settings.secret_key,
    access_token_expire_time=settings.jwt.access_token_expire_time,
    refresh_token_expire_time=settings.jwt.refresh_token_expire_time,
)

anno_backend = AnnoSessionBackend(session_name="th-session", secure=False)
jwt_backend = JWTBackend(jwt_service)
