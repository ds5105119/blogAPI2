from src.core.dependencies.fiscal import FiscalDataManager


class FiscalRepository:
    def __init__(self, fiscal_data_manager: FiscalDataManager):
        self.fiscal_data_manager = fiscal_data_manager

    @staticmethod
    def _duration_to_str(start_year: int | str | None, end_year: int | str | None) -> tuple[str | None, str | None]:
        if isinstance(start_year, int):
            start_year = str(start_year)
        if isinstance(end_year, int):
            end_year = str(end_year)

        return start_year, end_year

    def get_all_sum_by_year(self, start_year: int | str | None, end_year: int | str | None) -> dict:
        start_year, end_year = self._duration_to_str(start_year, end_year)

        df = self.fiscal_data_manager.year__sum.loc[start_year:end_year].to_dict()
        return df

    def get_all_pct_by_year(self, start_year: int | str | None, end_year: int | str | None) -> dict:
        start_year, end_year = self._duration_to_str(start_year, end_year)

        df = self.fiscal_data_manager.year__pct.loc[start_year:end_year].to_dict()
        return df

    def get_offc_nm_sum_by_year(self, start_year: int | str | None, end_year: int | str | None) -> dict:
        start_year, end_year = self._duration_to_str(start_year, end_year)

        df = self.fiscal_data_manager.year__offc_nm__sum.loc[start_year:end_year].to_dict()
        return df

    def get_offc_nm_pct_by_year(self, start_year: int | str | None, end_year: int | str | None) -> dict:
        start_year, end_year = self._duration_to_str(start_year, end_year)

        df = self.fiscal_data_manager.year__offc_nm__pct.loc[start_year:end_year].to_dict()
        return df
