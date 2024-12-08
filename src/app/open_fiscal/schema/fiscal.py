from enum import Enum

from pydantic import BaseModel


class ModeEnum(str, Enum):
    sum = "sum"
    diff = "diff"
    pct = "pct"


class FiscalDto(BaseModel):
    start_year: int | str | None = None
    end_year: int | str | None = None
    mode: ModeEnum = "sum"
