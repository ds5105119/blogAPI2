import polars as pl

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

    @staticmethod
    def _filter_by_year(dataset: pl.LazyFrame, start_year: str | None, end_year: str | None) -> pl.LazyFrame:
        year_column = pl.col(dataset.collect_schema().names()[0])
        return dataset.filter(
            (year_column >= start_year if start_year else True) & (year_column <= end_year if end_year else True)
        )

    @staticmethod
    def _pagination(dataset: pl.LazyFrame, page: int, size: int) -> pl.LazyFrame:
        return dataset.slice(page * size, (page + 1) * size)

    def get_by_year(self, start_year: int | str | None, end_year: int | str | None) -> dict:
        start_year, end_year = self._duration_to_str(start_year, end_year)
        return (
            self._filter_by_year(self.fiscal_data_manager.by__year, start_year, end_year)
            .collect()
            .to_dict(as_series=False)
        )

    def get_by_year__offc_nm(self, start_year: int | str | None, end_year: int | str | None) -> dict:
        start_year, end_year = self._duration_to_str(start_year, end_year)
        return (
            self._filter_by_year(self.fiscal_data_manager.by__year__offc_nm, start_year, end_year)
            .collect()
            .to_dict(as_series=False)
        )
