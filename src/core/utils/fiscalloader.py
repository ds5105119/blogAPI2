import asyncio
import json
from datetime import datetime
from typing import Iterable
from urllib.parse import urljoin

import httpx
import pandas as pd

from src.core.config import settings


class FiscalDataLoader:
    """
    A utility class for loading fiscal data from Open Fiscal Data API.

    This class provides methods to fetch and process fiscal expenditure data
    with support for parallel data retrieval and comprehensive error handling.
    """

    def __init__(self, base_url: str, path: str, save_key_prefix: str | None = None, timeout: int = 30):
        """
        Initialize the FiscalDataLoader with configurable parameters.

        Args:
            base_url (str): Base URL for the fiscal data API
            path (str): Specific API endpoint path
        """
        self.base_url = base_url
        self.path = path
        self.url = urljoin(self.base_url, self.path)
        self._save_key_prefix = save_key_prefix or path
        self._timeout = timeout

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
            response = await client.get(self.url, params=params, follow_redirects=True)
            data = json.loads(response.json())
            return data[self.path][0]["head"][0]["list_total_count"]
        except (KeyError, IndexError, json.JSONDecodeError) as e:
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

        async def fetch():
            try:
                response = await client.get(self.url, params=params, follow_redirects=True)
                data = json.loads(response.json())[self.path][1]["row"]
                return pd.DataFrame(data)
            except (KeyError, IndexError):
                return pd.DataFrame()

        try:
            return await fetch()
        except (json.JSONDecodeError, httpx.ReadTimeout):
            await asyncio.sleep(1)
            return await fetch()

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
            year (str or int): Fiscal year to retrieve data
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
        return consolidated_df

    def get_from_cache(self, cache, key: str):
        pass

    def _fetchall_from_cache(self, years: Iterable[int]):
        """
        Fetch existing data from the cache

        Parameters:
            years: years to retrieve data

        Returns:
            dict of years and data
        """
        results = {year: self.get_from_cache(None, f"{self._save_key_prefix}{year}") for year in years}
        results = {k: v for k, v in results.items() if v}

        return results

    async def _fetchall_from_url(self, years: Iterable[int]):
        """
        Fetch existing data from the Financial Information Disclosure System

        Parameters:
            years: years to retrieve data

        Returns:
            dict of years and data
        """
        client = httpx.AsyncClient(timeout=self._timeout)
        data_availability = await self.scan_data_availability(
            client,
            start_year=min(years),
            end_year=max(years),
        )

        tasks = (
            self.get_from_url(
                client,
                year=year,
                total_records=count,
            )
            for year, count in data_availability.items()
        )
        results = await asyncio.gather(*tasks)

        await client.aclose()
        return {k: v for k, v in zip(data_availability.keys(), results) if not v.empty}

    async def get_data(self, start_year: int | None = None, end_year: int | None = None) -> pd.DataFrame:
        """
        비동기적으로 열린재정 공개시스템의 데이터를 가져오는 함수

        Parameters:
            start_year (int): 집계를 시작할 연도, 기본갑 30년 전
            end_year (int): 집계를 종료할 연도, 기본값 내년

        Returns:
            수집된 데이터를 self.data에 저장한 뒤, self.data 반환
        """
        current_year = datetime.now().year
        start_year = start_year or current_year - 30
        end_year = end_year or current_year + 1
        years = set(range(start_year, end_year + 1))

        # fetch from cache
        data = self._fetchall_from_cache(years)

        # fetch from server
        data.update(await self._fetchall_from_url(years - set(data.keys())))

        df = pd.concat(data.values())
        return df
