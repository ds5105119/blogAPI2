from src.app.open_fiscal.repository.fiscal import FiscalRepository
from src.app.open_fiscal.schema.fiscal import FiscalDto


class FiscalService:
    def __init__(self, repository: FiscalRepository):
        self.repository = repository

    def get_fiscal(self, data: FiscalDto):
        mode = data.mode

        if mode == "sum":
            return self.repository.get_all_sum_by_year(data.start_year, data.end_year)
        elif mode == "pct":
            return self.repository.get_all_pct_by_year(data.start_year, data.end_year)
