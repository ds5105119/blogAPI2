from abc import abstractmethod
from typing import Any, Dict, List

import pandas as pd

from src.app.open_fiscal.test import FiscalDataManager


class BaseAggregator(FiscalDataManager):
    """Base class for fiscal data aggregation."""

    def __init__(self, start_year: int, end_year: int):
        super().__init__(start_year=start_year, end_year=end_year)

    def aggregate(self) -> pd.DataFrame:
        aggregated_data = self.data.pivot_table(
            index=["OFFC_NM"],
            columns=["FSCL_YY"],
            values=["Y_YY_MEDI_KCUR_AMT"],
            aggfunc="sum",
        )
        return aggregated_data

class BudgetByYear(BaseAggregator):
    """Aggregates budget data by year."""

    @staticmethod
    def calculate_yoy_change(df: pd.DataFrame) -> pd.DataFrame:
        """Calculates year-over-year percentage changes."""

        return (df.diff(axis=1) / df.shift(axis=1).replace(0, pd.NA)) * 100

class BudgetDataFormatter:
    """Analyzes budget changes and formats results."""

    @staticmethod
    def format_percentage(x: float) -> str:
        """Formats a number as a percentage string."""

        if isinstance(x, (int, float)):
            return f"+{x:.2f}%" if x > 0 else (f"{x:.2f}%" if x < 0 else "NaN")
        return "NaN"

    @staticmethod
    def sort_yearly_budgets(budget_data: pd.DataFrame) -> Dict[str, pd.Series]:
        sorted_budgets = {}
        for year in budget_data.columns.levels[1]:
            year_data = budget_data[("Y_YY_MEDI_KCUR_AMT", year)]
            sorted_budgets[f"{year}_asc"] = year_data.sort_values(ascending=True)
            sorted_budgets[f"{year}_desc"] = year_data.sort_values(ascending=False)
        return sorted_budgets

class BudgetAnalysisService:
    """Provides budget analysis services."""

    def __init__(self, start_year: int, end_year: int):
        self.ministry_aggregator = BaseAggregator(start_year, end_year)
        self.year_aggregator = BudgetByYear(start_year, end_year)
        self.change_formatter = BudgetDataFormatter()

    def get_ministry_budget_trends(self) -> Dict[str, pd.DataFrame]:
        budget_data_by_ministry = self.ministry_aggregator.aggregate()
        changes_yoy = self.year_aggregator.calculate_yoy_change(
            budget_data_by_ministry
        ).map(self.change_formatter.format_percentage)
        sorted_budgets = self.change_formatter.sort_yearly_budgets(budget_data_by_ministry)

        return {
            "budget_by_ministry": budget_data_by_ministry,
            "changes_yoy": changes_yoy,
            "sorted_budgets": sorted_budgets,
        }


service = BudgetAnalysisService(2024, 2025)
result = service.get_ministry_budget_trends()

# 기존 변화율 저장
result["changes_yoy"].to_csv("changes_yoy.csv", encoding="utf-8-sig", index=True)

# 정렬된 데이터 저장
# for year_order, data in result["sorted_budgets"].items():
#     data.to_csv(f"budget_{year_order}.csv", encoding="utf-8-sig", index=True)

print("csv 저장완료.")
