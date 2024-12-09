from typing import Annotated

from fastapi import Query

from src.app.open_fiscal.repository.fiscal import FiscalRepository
from src.app.open_fiscal.schema.fiscal import FiscalDto


class FiscalService:
    def __init__(self, repository: FiscalRepository):
        self.repository = repository

    def get_fiscal(self, data: Annotated[FiscalDto, Query()]):
        if data.level == data.level.by_year:
            return self.repository.get_by_year(data.start_year, data.end_year)
        else:
            return self.repository.get_by_year__offc_nm(data.start_year, data.end_year)
