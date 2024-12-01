import asyncio
import json
from datetime import datetime
from typing import Iterable

import httpx
import pandas as pd
import requests

from src.core.config import settings


class FiscalDataLoader:
    """
    A utility class for loading fiscal data from Open Fiscal Data API.

    This class provides methods to fetch and process fiscal expenditure data
    with support for parallel data retrieval and comprehensive error handling.
    """

    def __init__(self, base_url: str, path: str):
        """
        Initialize the FiscalDataLoader with configurable parameters.

        Args:
            base_url (str): Base URL for the fiscal data API
            path (str): Specific API endpoint path
        """
        self.base_url = base_url
        self.path = path

    @staticmethod
    def _create_request_params(year: str | int, index: str | int = "1", size: str | int = "1") -> dict[str, str]:
        """
        Generate API request parameters.

        Args:
            year (str or int): Fiscal year to retrieve data for
            index (str): Page index for pagination
            size (str): Number of records per page

        Returns:
            Dict containing API request parameters
        """
        return {
            "Key": settings.open_fiscal_data_api.key,
            "Type": "json",
            "pIndex": str(index),
            "pSize": str(size),
            "FSCL_YY": str(year),
        }

    @staticmethod
    def _get_url_data(url: str, path: str, params: dict) -> dict:
        result = requests.get(url + path, params=params)
        result = result.json()
        result = json.loads(result)
        result = result[path][1]["row"]
        return result

    async def _fetch_total_record_count(self, params: dict[str, str], client: httpx.AsyncClient) -> int:
        """
        Retrieve the total number of records for a given year.

        Args:
            params (Dict): API request parameters
            client (httpx.AsyncClient): Client for HTTP requests

        Returns:
            int: Total number of records

        Raises:
            ValueError: If data cannot be retrieved
        """
        try:
            response = await client.get(f"{self.base_url}{self.path}", params=params)
            data = json.loads(response.json())
            return data[self.path][0]["head"][0]["list_total_count"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unable to retrieve data: {e}")

    async def _fetch_page_data(self, params: dict[str, str], client: httpx.AsyncClient) -> pd.DataFrame:
        """
        Fetch a single page of fiscal data.

        Args:
            params (Dict): API request parameters
            client (httpx.AsyncClient): Client for HTTP requests

        Returns:
            pd.DataFrame: DataFrame containing fiscal data for a page
        """
        try:
            response = await client.get(f"{self.base_url}{self.path}", params=params)
            data = json.loads(response.json())[self.path][1]["row"]
            return pd.DataFrame(data)
        except (KeyError, IndexError):
            return pd.DataFrame()

    async def scan_data_availability(
        self,
        client: httpx.AsyncClient,
        start_year: int,
        end_year: int,
    ) -> dict[int, int]:
        """
        Scan fiscal data availability across multiple years.

        Args:
            client (httpx.AsyncClient): Client for HTTP requests
            start_year (int): Number of years to scan start
            end_year (int): Number of years to scan end

        Returns:
            Dict mapping available years to their record counts
        """

        async def check_year_data(year: int) -> tuple | None:
            try:
                params = self._create_request_params(year)
                return year, await self._fetch_total_record_count(params, client)
            except ValueError:
                return None

        tasks = (check_year_data(year) for year in range(start_year, end_year + 1))
        responses = await asyncio.gather(*tasks)

        results = {res[0]: res[1] for res in responses if res is not None}
        return results

    async def get_from_url(
        self,
        client: httpx.AsyncClient,
        year: str | int,
        page_size: int = 1000,
        total_records: int | None = None,
    ) -> pd.DataFrame:
        """
        Retrieve fiscal data for a specific year using parallel processing.

        Args:
            client (httpx.AsyncClient): Client for HTTP requests
            year (str or int): Fiscal year to retrieve data for
            page_size (int): Number of records to fetch per page
            total_records (int): Number of total records

        Returns:
            pd.DataFrame: Consolidated fiscal data sorted by office name and amount
        """
        params = self._create_request_params(year)
        total_records = total_records or await self._fetch_total_record_count(params, client)

        page_params = (
            self._create_request_params(year, index=str(page), size=str(page_size))
            for page in range(1, total_records // page_size + 2)
        )
        tasks = (self._fetch_page_data(params, client) for params in page_params)
        dataframes = await asyncio.gather(*tasks)

        consolidated_df = pd.concat(dataframes, ignore_index=True)
        consolidated_df = consolidated_df.sort_values(
            by=[
                "OFFC_NM",
                "Y_YY_MEDI_KCUR_AMT",
                "Y_YY_DFN_MEDI_KCUR_AMT",
            ],
            ignore_index=True,
        )

        return consolidated_df

    def get_from_cache(self, key: str) -> pd.DataFrame:
        pass


class FiscalDataManager:
    def __init__(
        self,
        base_url: str = "https://openapi.openfiscaldata.go.kr/",
        path: str = "ExpenditureBudgetInit5",
        start_year: int | None = None,
        end_year: int | None = None,
        save_key_prefix: str | None = None,
        loader: FiscalDataLoader | None = None,
    ):
        current_year = datetime.now().year
        self.start_year = start_year or current_year - 30
        self.end_year = end_year or current_year + 1
        self.loader = loader or FiscalDataLoader(base_url, path)
        self.save_key_prefix = save_key_prefix or path
        self.data = self.sync_get_data(self.start_year, self.end_year)

    def _get_from_cache(self, years: Iterable[int]):
        results = {year: self.loader.get_from_cache(f"{self.save_key_prefix}{year}") for year in years}
        results = {k: v for k, v in results.items() if v}

        return results

    async def _get_from_url(self, years: Iterable[int]):
        client = httpx.AsyncClient(timeout=20.0)
        data_availability = await self.loader.scan_data_availability(
            client,
            start_year=min(years),
            end_year=max(years),
        )

        tasks = (
            self.loader.get_from_url(
                client,
                year=year,
                total_records=count,
            )
            for year, count in data_availability.items()
        )
        results = await asyncio.gather(*tasks)

        await client.aclose()
        return {k: v for k, v in zip(data_availability.keys(), results) if not v.empty}

    async def get_data(self, start_year: int, end_year: int) -> pd.DataFrame:
        years = set(range(start_year, end_year + 1))

        data = self._get_from_cache(years)
        data.update(await self._get_from_url(years - set(data.keys())))
        data = pd.concat(data.values(), keys=data.keys())

        return data

    def sync_get_data(self, start_year: int, end_year: int) -> pd.DataFrame:
        return asyncio.run(self.get_data(start_year, end_year))
