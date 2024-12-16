from itertools import chain, product
from typing import Annotated, Hashable, Self, Sequence

import polars as pl
from fastapi import Query
from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: int | None = Field(1, ge=1, description="Page number")
    size: int | None = Field(50, ge=1, le=100, description="Page size")


PageQuery = Annotated[PageParams, Query()]


class Table:
    def __init__(self, table: dict[tuple, list]):
        self.table: dict[tuple, list] = table
        self._raw_keys = list(self.table.keys())
        self._key_count = 0 if len(self._raw_keys) == 0 else len(self._raw_keys[0])
        self.keys = [{key[i] for key in self._raw_keys} for i in range(self._key_count)]
        self.total = None
        self.previous_page = None
        self.next_page = None
        self.page_size = None

    def __repr__(self):
        return self.table.__repr__()

    def index(self, stmt: Sequence[Sequence[Hashable]], page: int | None = None, size: int | None = None) -> Self:
        if len(self._raw_keys[0]) < len(stmt):
            raise IndexError

        if page is None and size is None:
            table = {k: self.table.get(k) for k in product(*stmt, *self.keys[len(stmt) :])}
            table = {k: v for k, v in table.items() if v is not None}
            table = Table(table)

        elif page is not None and size is not None:
            table = self.page_index(stmt, page, size)

        else:
            raise ValueError("Page and size must be specified")

        return table

    def page_index(self, stmt: Sequence[Sequence[Hashable]], page: int, size: int):
        keys = sorted(tuple(set(product(*stmt, *self.keys[len(stmt) :])).intersection(self._raw_keys)))
        table = {k: self.table.get(k) for k in keys[(page - 1) * size : page * size]}
        table = Table(table)

        table.total = len(keys)
        table.previous_page = page - 1 if page > 2 else None
        table.next_page = page + 1 if page * size < len(keys) else None
        table.page_size = len(table.table)
        return table

    def to_dicts(self):
        if self.total is None:
            return list(chain(*self.table.values()))

        return {
            "total": self.total,
            "previousPage": self.previous_page,
            "nextPage": self.next_page,
            "pageSize": self.page_size,
            "items": list(chain(*self.table.values())),
        }


def group_by_frame_to_table(frame: pl.LazyFrame | pl.DataFrame, *col: str) -> Table:
    if isinstance(frame, pl.LazyFrame):
        frame = frame.collect()

    fields = [sorted(set(frame.select(name).to_series())) for name in col]
    table = {desc: frame.filter(**dict(zip(col, desc))).to_dicts() for desc in product(*fields)}
    table = {k: v for k, v in table.items() if v}

    return Table(table)
