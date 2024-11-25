from sqlite3 import IntegrityError
from typing import Any, Generic, Iterable, Sequence, Type, TypeVar, cast

from sqlalchemy import UUID, Column, Label, MetaData, Result, Row, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)
_P = Result[tuple[Any]]


class BaseRepository[T]:
    model: type[T]
    session: AsyncSession

    def __init__(self, model: type[T]):
        self.model = model

    def get_columns(self, columns: list[str] | None) -> list:
        if columns:
            return [getattr(self.model, column) for column in columns]
        return [self.model]


class BaseCreateRepository[T](BaseRepository[T]):
    async def _create(self, session: AsyncSession, **kwargs: Any) -> T:
        session.add(entity := self.model(**kwargs))
        await session.commit()
        await session.refresh(entity)

        return entity

    async def _bulk_create(self, session: AsyncSession, kwargs: Sequence[dict[str, Any]]) -> None:
        stmt = insert(self.model).values(kwargs)
        await session.execute(stmt)
        await session.commit()

    async def create(self, session: AsyncSession, *args: Any, **kwargs: Any) -> T | None:
        if args:
            return await self._bulk_create(session, list(args))
        elif kwargs:
            return await self._create(session, **kwargs)
        else:
            raise ValueError("Invalid arguments for creation.")


class BaseReadRepository[T](BaseRepository[T]):
    async def get(self, session: AsyncSession, id: int | str, columns: list[str] | None = None) -> _P:
        columns = self.get_columns(columns)
        stmt = select(*columns).where(cast("ColumnElement[bool]", self.model.id == id))
        result = await session.execute(stmt)

        return result

    async def filter_get(self, session: AsyncSession, filters: list, columns: list[str] | None = None) -> _P:
        columns = self.get_columns(columns)
        stmt = select(*columns).where(*filters)
        result = await session.execute(stmt)

        return result


class BaseUpdateRepository[T](BaseRepository[T]):
    async def update(self, db: AsyncSession, id: int | str, **kwargs) -> None:
        query = update(self.model).where(cast("ColumnElement[bool]", self.model.id == id)).values(**kwargs)
        await db.execute(query)
        await db.commit()

    async def filter_update(self, db: AsyncSession, filters: list, **kwargs) -> None:
        query = update(self.model).where(*filters).values(**kwargs)
        await db.execute(query)
        await db.commit()


class BaseDeleteRepository[T](BaseRepository[T]):
    async def _delete_single(self, db: AsyncSession, id: int | str) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id == id))
        await db.execute(stmt)
        await db.commit()

    async def _delete_multiple(self, db: AsyncSession, ids: list[int | str]) -> None:
        if not ids:
            return

        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id.in_(ids)))
        await db.execute(stmt)
        await db.commit()

    async def delete(self, db: AsyncSession, id: int | str | tuple[int | str] | list[int | str]) -> None:
        if isinstance(id, (int, str)):
            await self._delete_single(db, id)
        elif isinstance(id, (tuple, list)) and len(id):
            await self._delete_multiple(db, list(id))
        else:
            raise ValueError("'id' must be an int, str, or Iterable of int or str")
