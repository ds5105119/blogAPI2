from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, async_scoped_session

from app.core.config import settings


# pre_ping 활성화
postgres_engine = create_async_engine(
    settings.SQLALCHEMY_POSTGRES_URI,
    pool_pre_ping=True,
)

# scoped_session 활성화
SessionLocal = async_scoped_session(
    async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=postgres_engine
    )
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
