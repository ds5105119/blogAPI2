from app.core.config import settings
from app.db import AsyncDB
from webkit.auth import JWTService
from webkit.cache import RedisClient
from webkit.throttle.backend import JWTBackend

postgres = AsyncDB(settings.POSTGRES_DSN.unicode_string())
redis_client = RedisClient(settings.REDIS_DSN.unicode_string())
jwt_service = JWTService(redis_client, secret_key=settings.SECRET_KEY)
jwt_backend = JWTBackend(jwt_service)


print(jwt_service.create_access_token({"sub": "1"}))
