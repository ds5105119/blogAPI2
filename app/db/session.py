import asyncio
from typing import AsyncGenerator

from sqlalchemy import MetaData, exc
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine

from app.core.config import settings

metadata = MetaData()

# pre_ping 활성화
postgres_engine = create_async_engine(
    settings.SQLALCHEMY_POSTGRES_URI.unicode_string(),
    pool_pre_ping=True,
)

# scoped_session 활성화
async_session = async_scoped_session(
    session_factory=async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=postgres_engine),
    scopefunc=asyncio.current_task,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise error


async def init_db() -> None:
    async with postgres_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
