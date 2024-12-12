from enum import IntEnum
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class LevelEnum(IntEnum):
    by_year = 0
    by_name = 1


class FiscalDto(BaseModel):
    start_year: int | str | None = None
    end_year: int | str | None = None
    level: LevelEnum = LevelEnum.by_year
    page: int | None = Field(1, ge=1, description="Page number")
    size: int | None = Field(50, ge=1, le=100, description="Page size")


FiscalQuery = Annotated[FiscalDto, Query()]
