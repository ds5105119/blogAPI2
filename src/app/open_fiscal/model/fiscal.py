import polars as pl

from src.core.utils.openapi.datamanager import PolarsDataManager
from src.core.utils.polarshelper import Table, group_by_frame_to_table


class BaseFiscalData:
    def __init__(self, manager: PolarsDataManager):
        self.data = manager.data


class FiscalData(BaseFiscalData):
    def __init__(self, manager: PolarsDataManager):
        super().__init__(manager)
        self.department_no = {}
        self.by__year = Table({})
        self.by__year__offc_nm = Table({})
        self.manager = manager
        self.manager.register_callback(self._callback)

    def _callback(self):
        print("Manager data updated. Rebuilding FiscalData...")
        self.data = self.manager.data
        self.build()

    def build(self):
        self.department_no = {k: v for v, k in enumerate(set(self.data.select("OFFC_NM").to_series()))}

        mappings = self._get_mappings()
        for mapping in mappings:
            min_no = min([self.department_no[name] for name in mapping if self.department_no.get(name)])
            self.department_no.update({name: min_no for name in mapping})

        self.data = self.data.with_columns(
            pl.col("OFFC_NM")
            .map_elements(lambda x: self.department_no.get(x, None), return_dtype=pl.Int8)
            .alias("NORMALIZED_DEPT_NO")
        )

        self.by__year = self._by__year()
        self.by__year__offc_nm = self._by__year__offc_nm()

    @staticmethod
    def _get_mappings() -> list[list[str]]:
        return [
            ["문화재청", "국가유산청"],
            ["안전행정부", "행정자치부", "행정안전부"],
            ["미래창조과학부", "과학기술정보통신부"],
            ["국가보훈처", "국가보훈부"],
        ]

    def _by__year(self):
        lf = (
            self.data.group_by("FSCL_YY")
            .agg(pl.col("Y_YY_MEDI_KCUR_AMT").sum().alias("TOTAL_AMT"))
            .sort("FSCL_YY")
            .with_columns(pl.col("TOTAL_AMT").pct_change().alias("PCT_CHANGE"))
        )
        return group_by_frame_to_table(lf, "FSCL_YY")

    def _by__year__offc_nm(self):
        lf = (
            self.data.group_by(["FSCL_YY", "NORMALIZED_DEPT_NO", "OFFC_NM"])
            .agg(pl.col("Y_YY_MEDI_KCUR_AMT").sum().alias("TOTAL_AMT"))
            .sort(["NORMALIZED_DEPT_NO", "FSCL_YY"])
            .with_columns(pl.col("TOTAL_AMT").pct_change().over("NORMALIZED_DEPT_NO").alias("PCT_CHANGE"))
        )
        return group_by_frame_to_table(lf, "FSCL_YY", "NORMALIZED_DEPT_NO")
