from src.app.open_fiscal.repository.fiscal import FiscalRepository
from src.app.open_fiscal.schema.fiscal import FiscalQuery
from src.core.utils.polarshelper import PageQuery


class FiscalService:
    def __init__(self, repository: FiscalRepository):
        self.repository = repository

    def get_fiscal(self, data: FiscalQuery):
        if data.level == data.level.by_year:
            return self.repository.get_by_year(data.start_year, data.end_year, data.page, data.size)
        else:
            return self.repository.get_by_year__offc_nm(data.start_year, data.end_year, data.page, data.size)
