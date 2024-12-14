from datetime import datetime

from src.app.open_fiscal.model.fiscal import FiscalDataManager


class FiscalRepository:
    def __init__(self, fiscal_data_manager: FiscalDataManager):
        self.fiscal_data_manager = fiscal_data_manager

    @staticmethod
    def _duration_to_range(start_year: int | str | None, end_year: int | str | None) -> list[str]:
        if isinstance(start_year, str):
            start_year = int(start_year)
        if isinstance(end_year, str):
            end_year = int(end_year)

        if start_year is None:
            start_year = 2000

        if end_year is None:
            end_year = datetime.now().year + 1

        return [str(year) for year in range(start_year, end_year)]

    def get_by_year(
        self,
        start_year: int | str | None,
        end_year: int | str | None,
        page: int | None = None,
        size: int | None = None,
    ):
        years = self._duration_to_range(start_year, end_year)
        return self.fiscal_data_manager.by__year.index([years], page, size).to_dicts()

    def get_by_year__offc_nm(
        self,
        start_year: int | str | None,
        end_year: int | str | None,
        page: int | None = None,
        size: int | None = None,
    ):
        years = self._duration_to_range(start_year, end_year)
        return self.fiscal_data_manager.by__year__offc_nm.index([years], page, size).to_dicts()
