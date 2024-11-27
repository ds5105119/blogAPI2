from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from webtool.cache import RedisCache
from webtool.db import AsyncDB

from src.core.config import settings

Postgres = AsyncDB(settings.postgres_dsn.unicode_string())
Redis = RedisCache(settings.redis_dsn.unicode_string())

db_session = Annotated[AsyncSession, Depends(Postgres)]
