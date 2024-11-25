from webtool.cache import RedisCache
from webtool.db import AsyncDB

from app.core.config import settings

Postgres = AsyncDB(settings.postgres_dsn.unicode_string())
Redis = RedisCache(settings.redis_dsn.unicode_string())
