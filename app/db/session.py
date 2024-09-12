from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.core.config import settings


# pre_ping 활성화
postgres_engine = create_engine(
    settings.SQLALCHEMY_POSTGRES_URI,
    pool_pre_ping=True,
)

# scoped_session 활성화
SessionLocal = scoped_session(
    sessionmaker(
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
