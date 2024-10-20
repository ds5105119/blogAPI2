from sqlalchemy.orm import DeclarativeBase

from app.db.session import metadata


class Base(DeclarativeBase):
    metadata = metadata
