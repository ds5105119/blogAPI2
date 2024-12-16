from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import StaticPool
from webtool.cache import RedisCache
from webtool.db import AsyncDB

from src.core.config import settings

Postgres = AsyncDB(settings.postgres_dsn.unicode_string())
Redis = RedisCache(settings.redis_dsn.unicode_string())
MemorySqlite = AsyncDB(
    "sqlite+aiosqlite:///:memory:",
    engine_args={
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    },
)

postgres_session = Annotated[AsyncSession, Depends(Postgres)]
sqlite_session = Annotated[AsyncSession, Depends(MemorySqlite)]
