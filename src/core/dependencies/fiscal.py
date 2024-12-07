from functools import cached_property

import pandas as pd

from src.core.utils.fiscalloader import FiscalDataLoader


class BaseFiscalDataManager:
    def __init__(
        self,
        base_url: str,
        path: str,
        start_year: int | None = None,
        end_year: int | None = None,
        loader=FiscalDataLoader,
    ):
        self.data: pd.DataFrame = pd.DataFrame()
        self._start_year = start_year
        self._end_year = end_year
        self._loader = loader(base_url, path)

    async def init(self):
        self.data = await self._loader.get_data(self._start_year, self._end_year)


class FiscalDataManager(BaseFiscalDataManager):
    def __init__(
        self,
        base_url: str,
        path: str,
        start_year: int | None = None,
        end_year: int | None = None,
        loader=FiscalDataLoader,
    ):
        super().__init__(base_url, path, start_year, end_year, loader)

        self.department_no = {}

    async def init(self):
        await super().init()

        self.department_no = {k: v for v, k in enumerate(set(self.data["OFFC_NM"]))}

        mappings = self._get_mappings()
        for mapping in mappings:
            min_no = min([self.department_no[name] for name in mapping])
            self.department_no.update({name: min_no for name in mapping})

        self.data["NORMALIZED_DEPT_NO"] = self.data["OFFC_NM"].apply(lambda x: self.department_no[x])

    def _get_mappings(self) -> list[list[str]]:
        return [
            ["문화재청", "국가유산청"],
            ["안전행정부", "행정자치부", "행정안전부"],
            ["미래창조과학부", "과학기술정보통신부"],
            ["국가보훈처", "국가보훈부"],
        ]

    @cached_property
    def year__sum(self):
        return self.data.pivot_table(values=["Y_YY_MEDI_KCUR_AMT"], index=["FSCL_YY"], aggfunc="sum")

    @cached_property
    def year__pct(self):
        return self.data.pivot_table(
            values=["Y_YY_MEDI_KCUR_AMT"],
            index=["FSCL_YY"],
            aggfunc="sum",
        ).pct_change()

    @cached_property
    def year__diff(self):
        return self.data.pivot_table(
            values=["Y_YY_MEDI_KCUR_AMT"],
            index=["FSCL_YY"],
            aggfunc="sum",
        ).diff()

    @cached_property
    def year__offc_nm__sum(self):
        return self.data.pivot_table(
            values=["Y_YY_MEDI_KCUR_AMT"],
            index=["FSCL_YY", "OFFC_NM"],
            aggfunc="sum",
        )

    @cached_property
    def year__offc_nm__pct(self):
        return (
            self.data.pivot_table(
                values=["Y_YY_MEDI_KCUR_AMT"],
                index=["FSCL_YY", "NORMALIZED_DEPT_NO", "OFFC_NM"],
                aggfunc="sum",
            )
            .groupby(level=1)
            .pct_change()
        )

    @cached_property
    def year__offc_nm__diff(self):
        return (
            self.data.pivot_table(
                values=["Y_YY_MEDI_KCUR_AMT"],
                index=["FSCL_YY", "NORMALIZED_DEPT_NO", "OFFC_NM"],
                aggfunc="sum",
            )
            .groupby(level=1)
            .diff()
        )


fiscal_data_manager = FiscalDataManager(
    base_url="https://openapi.openfiscaldata.go.kr",
    path="ExpenditureBudgetInit5",
)
