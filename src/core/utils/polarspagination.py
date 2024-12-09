from typing import Any, Generic, Self, TypeVar

import polars as pl
from fastapi import Query
from fastapi_pagination.api import apply_items_transformer, create_page
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.types import AdditionalData, ItemsTransformer
from pydantic import BaseModel, Field

T = TypeVar("T", bound=pl.LazyFrame)


def _get_lazf_length(dataset: pl.LazyFrame):
    return dataset.select(pl.len()).collect().item()


def _paginated_lazf(dataset: pl.LazyFrame, params: RawParams) -> list:
    return dataset.slice(params.offset, params.limit).collect().to_dicts()


class LazyFrameParams(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size if self.size is not None else None,
            offset=self.size * (self.page - 1) if self.page is not None and self.size is not None else None,
        )


class LazyFramePage(AbstractPage[T], Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    pageSize: int = Field(ge=0)
    nextPage: int | None = Field(ge=1)

    __params_type__ = LazyFrameParams

    @classmethod
    def create(cls, items: T, params: LazyFrameParams, *, total: int | None = None, **kwargs: Any) -> Self:
        page_size = len(items)
        next_offset = params.page * page_size

        if next_offset >= total:
            next_page = None
        else:
            next_page = params.page + 1

        return cls(
            total=total,
            items=items,
            pageSize=page_size,
            nextPage=next_page,
        )


def verify_params(params: LazyFrameParams | None) -> tuple[LazyFrameParams, RawParams]:
    from fastapi_pagination.api import resolve_params

    params = resolve_params(params)
    raw_params = params.to_raw_params()

    if raw_params.type != "limit-offset":
        raise ValueError(f"{raw_params.type!r} params not supported")

    return params, raw_params


async def paginate(
    sequence: T,
    params: LazyFrameParams | None = None,
    *,
    transformer: ItemsTransformer | None = None,
    additional_data: AdditionalData | None = None,
) -> Any:
    params, raw_params = verify_params(params)

    items = _paginated_lazf(sequence, raw_params)
    t_items = await apply_items_transformer(items, transformer, async_=True)
    total = _get_lazf_length(sequence)

    return create_page(
        t_items,
        total=total,
        params=params,
        **(additional_data or {}),
    )
