from enum import IntEnum
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class LevelEnum(IntEnum):
    by_year = 0
    by_name = 1


class FiscalDto(BaseModel):
    start_year: int | str | None = None
    end_year: int | str | None = None
    level: LevelEnum = LevelEnum.by_year


FiscalQuery = Annotated[FiscalDto, Query()]
