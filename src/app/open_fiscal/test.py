import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import requests

from src.core.config import settings


class FiscalDataLoader:
    @staticmethod
    def _get_url_params(year: str, index: str = "1", size: str = "1"):
        return {
            "Key": settings.open_fiscal_data_api.key,
            "Type": "json",
            "pIndex": index,
            "pSize": size,
            "FSCL_YY": year,
        }

    @staticmethod
    def _get_url_data_len(url: str, path: str, params: dict) -> bool:
        head = requests.get(url + path, params=params)
        head = json.loads(head.json())

        try:
            data = head[path][0]["head"]
            data_len = data[0]["list_total_count"]
        except KeyError:
            raise ValueError("CAN NOT FIND DATA")

        return data_len

    @staticmethod
    def _get_url_data(url: str, path: str, params: dict) -> dict:
        result = requests.get(url + path, params=params)
        result = result.json()
        result = json.loads(result)
        result = result[path][1]["row"]
        return result

    def get_from_url(
        self,
        year: str | int,
        url: str = "https://openapi.openfiscaldata.go.kr/",
        path: str = "ExpenditureBudgetInit5",
        data_len: int | None = None,
    ) -> pd.DataFrame:
        year = year if isinstance(year, str) else str(year)
        df = pd.DataFrame()

        data_len = data_len or self._get_url_data_len(url, path, self._get_url_params(year))
        params_generator = (
            self._get_url_params(
                year,
                index=str(i),
                size="1000",
            )
            for i in range(1, data_len // 1000 + 2)
        )

        def get_data(params: dict):
            result = self._get_url_data(url, path, params)
            return pd.DataFrame(result)

        with ThreadPoolExecutor(max_workers=10) as executor:
            data = executor.map(get_data, params_generator)
        data = list(data)

        df = pd.concat([df, *data])
        df = df.sort_values(
            by=["OFFC_NM", "Y_YY_DFN_MEDI_KCUR_AMT"],
            ignore_index=True,
        )

        return df

    def scan_url(
        self,
        url: str = "https://openapi.openfiscaldata.go.kr/",
        path: str = "ExpenditureBudgetInit5",
        period: int = 30,
    ) -> dict:
        current_year = datetime.now().year
        year_range = list(range(current_year - period, current_year + 2))
        params_generator = (self._get_url_params(year) for year in year_range)

        def has_data(params: dict):
            try:
                return self._get_url_data_len(url, path, params)
            except ValueError:
                return 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            data_lengths = executor.map(has_data, params_generator)
        data_lengths = list(data_lengths)

        results = zip(year_range, data_lengths)
        results = {year: length for year, length in results if length}
        return results

    def get_from_cache(self, key) -> pd.DataFrame:
        pass


x = FiscalDataLoader()
print(x.get_from_url("2024"))
