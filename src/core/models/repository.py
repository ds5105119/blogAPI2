from typing import Any, Sequence, TypeVar, cast

from sqlalchemy import Result, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)
_P = Result[tuple[Any]]


class BaseRepository[T]:
    model: type[T]
    session: type[Session]

    def __init__(self, model: type[T]):
        self.model = model

    def get_columns(self, columns: list[str] | None) -> list:
        if columns:
            return [getattr(self.model, column) for column in columns]
        return [self.model]


class BaseCreateRepository[T](BaseRepository[T]):
    async def _create(self, session: Session, **kwargs: Any) -> T:
        session.add(entity := self.model(**kwargs))
        await session.commit()
        await session.refresh(entity)

        return entity

    async def _bulk_create(self, session: Session, kwargs: Sequence[dict[str, Any]]) -> None:
        stmt = insert(self.model).values(kwargs)
        await session.execute(stmt)
        await session.commit()

    async def create(self, session: Session, values: Sequence[dict[str, Any]] | None = None, **kwargs: Any) -> T | None:
        if kwargs:
            return await self._create(session, **kwargs)
        elif values:
            return await self._bulk_create(session, values)
        else:
            raise ValueError("Invalid arguments for creation.")


class BaseReadRepository[T](BaseRepository[T]):
    async def get(self, session: Session, filters: Sequence, columns: list[str] | None = None) -> _P:
        columns = self.get_columns(columns)
        stmt = select(*columns).where(*filters)
        result = await session.execute(stmt)

        return result

    async def get_by_id(self, session: Session, id: int | str, columns: list[str] | None = None) -> _P:
        columns = self.get_columns(columns)
        stmt = select(*columns).where(cast("ColumnElement[bool]", self.model.id == id))
        result = await session.execute(stmt)

        return result


class BaseUpdateRepository[T](BaseRepository[T]):
    async def filter(self, db: Session, filters: Sequence, **kwargs) -> None:
        query = update(self.model).where(*filters).values(**kwargs)
        await db.execute(query)
        await db.commit()

    async def update_by_id(self, db: Session, id: int | str, **kwargs) -> None:
        query = update(self.model).where(cast("ColumnElement[bool]", self.model.id == id)).values(**kwargs)
        await db.execute(query)
        await db.commit()


class BaseDeleteRepository[T](BaseRepository[T]):
    async def _delete(self, db: Session, id: int | str) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id == id))
        await db.execute(stmt)
        await db.commit()

    async def _bulk_delete(self, db: Session, ids: list[int | str]) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id.in_(ids)))
        await db.execute(stmt)
        await db.commit()

    async def delete(self, db: Session, id: int | str | tuple[int | str] | list[int | str]) -> None:
        if isinstance(id, (int, str)):
            await self._delete(db, id)
        elif isinstance(id, (tuple, list)) and len(id):
            await self._bulk_delete(db, list(id))
        else:
            raise ValueError("'id' must be an int, str, or Iterable of int or str")
