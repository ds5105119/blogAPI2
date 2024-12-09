from typing import Any, Generic, Optional, TypeVar

import polars as pl
from fastapi import Query
from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from pydantic import BaseModel
from typing_extensions import Self

T = TypeVar("T", bound=pl.LazyFrame)


class LazyFrameParams(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size if self.size is not None else None,
            offset=self.size * (self.page - 1) if self.page is not None and self.size is not None else None,
        )


class LazyFramePage(AbstractPage[T], Generic[T]):
    results: list[T]
    totalResults: int

    __params_type__ = Params

    @staticmethod
    def get_lazf_length(dataset: pl.LazyFrame):
        return dataset.select(pl.len()).collect().item()

    @staticmethod
    def _pagination(dataset: pl.LazyFrame, page: int, size: int) -> pl.LazyFrame:
        return dataset.slice((page - 1) * size, size)

    @classmethod
    def create(cls, items: T, params: LazyFrameParams, *args, **kwargs: Any) -> Self:
        total = cls.get_lazf_length(items)

        return cls(
            results=items,
            totalResults=total,
        )


page = LazyFramePage[int].create(range(100), Params())
print(page.model_dump_json(indent=4))
