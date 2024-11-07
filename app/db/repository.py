from typing import Any, Generic, Iterable, Sequence, Type, TypeVar

from sqlalchemy import Label, Result, Row, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.entity import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    entity: Type[T]
    session: AsyncSession

    def __init__(self, entity: Type[T]):
        self.entity = entity

    @property
    def table(self):
        return Base.metadata.tables[self.entity.__tablename__]

    def get_columns(self, columns: list[str] | None = None) -> list:
        """
        Retrieves the columns specified in the 'columns' parameter.
        """
        if columns:
            return [getattr(self.entity, column) for column in columns]
        return [self.entity]


class BaseCreateRepository(BaseRepository[T]):
    async def create(self, session: AsyncSession, **kwargs) -> T:
        session.add(entity := self.entity(**kwargs))
        await session.commit()
        await session.refresh(entity)

        return entity

    async def bulk_create(self, db: AsyncSession, data_list: list[dict]) -> None:
        stmt = insert(self.entity).values(data_list)
        await db.execute(stmt)
        await db.commit()


class BaseReadRepository(BaseRepository[T]):
    async def find_by_id(
        self, session: AsyncSession, id: int | str, columns: list[str] | None = None
    ) -> Sequence[Row[tuple[Any]]]:
        columns = self.get_columns(columns)
        stmt = select(*columns).filter(self.entity.id == id)
        result = await session.execute(stmt)

        return result.fetchall()


class BaseDeleteRepository(BaseRepository[T]):
    async def _delete_single(self, db: AsyncSession, id: int | str) -> None:
        stmt = delete(self.entity).where(self.entity.id == id)
        await db.execute(stmt)
        await db.commit()

    async def _delete_multiple(self, db: AsyncSession, ids: list[int | str]) -> None:
        if not ids:
            return

        stmt = delete(self.entity).where(self.entity.id.in_(ids))
        await db.execute(stmt)
        await db.commit()

    async def delete(self, db: AsyncSession, id: int | str | tuple[int | str] | list[int | str]) -> None:
        if isinstance(id, (int, str)):
            await self._delete_single(db, id)
        elif isinstance(id, (tuple, list)) and len(id):
            await self._delete_multiple(db, list(id))
        else:
            raise ValueError("'ids' must be an int, str, or Iterable of int or str")
