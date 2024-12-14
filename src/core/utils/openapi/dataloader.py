import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from math import ceil

import httpx


@dataclass
class ApiConfig:
    security_definitions_type: str = "type"
    security_definitions_name: str = "name"
    security_definitions_method: str = "in"
    security_definitions: str = "securityDefinitions"

    api_path: str = "paths"
    api_parameters: str = "parameters"
    api_parameters_name: str = "name"
    api_parameters_required: str = "required"

    header: str = "header"
    query: str = "query"

    request_page: str = "page"
    request_size: str = "perPage"
    request_default_key: str = "Key"
    request_year: str = "FSCL_YY"

    response_page: str = "page"
    response_per_page: str = "perPage"
    response_total_count: str = "totalCount"
    response_current_count: str = "currentCount"
    response_match_count: str = "matchCount"
    response_data: str = "data"


class BaseOpenDataLoader(ABC):
    base_url: str
    swagger_url: str
    api_key: str | None

    @abstractmethod
    async def get_data(self, path: str, params: dict | None = None) -> dict | list[dict]:
        pass


class OpenDataLoader(BaseOpenDataLoader):
    def __init__(
        self,
        base_url: str,
        swagger_url: str | None = None,
        api_key: str | None = None,
        paths: dict | None = None,
        batch_size: int = 1000,
        concurrency_limit: int = 20,
        timeout: int = 30,
        api_config: ApiConfig | None = None,
    ):
        """
        Initialize the FiscalDataLoader with configurable parameters.

        Args:
            base_url (str):
            swagger_url (str):
            api_key (str):
            paths (dict):
            batch_size (int):
            timeout (int):
            api_config (ApiConfig):
        """
        self.base_url = base_url
        self.swagger_url = swagger_url
        self.api_key = api_key

        self.headers = {}
        self.query_params = {}
        self.paths = paths or {}

        self._timeout = timeout
        self._batch_size = batch_size
        self._concurrency_limit = concurrency_limit
        self._api_config = api_config or ApiConfig()

    def get_client(self):
        return httpx.AsyncClient(
            headers=self.headers,
            timeout=self._timeout,
            base_url=self.base_url,
            params=self.query_params,
            follow_redirects=True,
        )

    async def get_docs(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=self.swagger_url)
        return response.json()

    def apply_docs(self, docs: dict):
        self.paths.update(docs.get(self._api_config.api_path, {}))

        if not self.api_key:
            return

        security_definitions = docs.get(self._api_config.security_definitions, {})

        for security_definition in security_definitions.values():
            method = security_definition.get(self._api_config.security_definitions_method, "")
            name = security_definition.get(self._api_config.security_definitions_name, "")

            if method == self._api_config.header:
                self.headers[name] = self.api_key

            if method == self._api_config.query:
                self.query_params[name] = self.api_key

    async def fetch_data(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict | None = None,
    ) -> dict:
        params = {} if params is None else params

        _path: dict | None = self.paths.get(path, None)
        if _path is None:
            raise ValueError("해당 경로를 찾을 수 없습니다.")

        _method = tuple(_path.keys())
        if not _method:
            raise ValueError("요청을 보낼 수 없는 경로입니다.")
        _method = _method[0]

        _parameters = _path[_method].get(self._api_config.api_parameters_name, {})
        _parameters_required = {
            v.get(self._api_config.api_parameters_name)
            for v in _parameters.values()
            if v.get(self._api_config.api_parameters_required, False)
        }
        if not _parameters_required.issubset(set(params.keys())):
            raise ValueError("필수 파라미터가 누락되었습니다.", _parameters_required)

        try:
            response = await getattr(client, _method)(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP 에러 발생: {e.response.status_code}, {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"요청 에러 발생: {str(e)}")

        try:
            data = response.json()
            return json.loads(data) if isinstance(data, str) else data
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Unable to retrieve data: {e}")

    async def fetch_total_record_count(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict,
    ) -> int:
        params[self._api_config.request_page] = 1
        params[self._api_config.request_size] = 1

        data = await self.fetch_data(client, path, params)
        data = data.get(self._api_config.response_total_count, 0)

        return data

    async def fetch_paginated_data(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict | None = None,
        semaphore: asyncio.Semaphore = None,
    ) -> list[dict]:
        params = {} if params is None else params
        total_count = await self.fetch_total_record_count(client, path, params)

        if not total_count:
            return []

        params[self._api_config.request_size] = self._batch_size

        async def fetch(page):
            async with semaphore if semaphore else asyncio.Semaphore(self._concurrency_limit):
                params[self._api_config.request_page] = page
                response = await self.fetch_data(client, path, params)
                return response.get(self._api_config.response_data)

        tasks = [fetch(page) for page in range(1, ceil(total_count / self._batch_size) + 1)]
        data = list(chain.from_iterable(await asyncio.gather(*tasks)))

        return data

    async def get_data(self, path: str, params: dict | None = None) -> dict | list[dict]:
        if self.swagger_url:
            docs = await self.get_docs()
            self.apply_docs(docs)

        params = {} if params is None else params
        semaphore = asyncio.Semaphore(self._concurrency_limit)

        async with self.get_client() as client:
            data = await self.fetch_paginated_data(client, path, params, semaphore)
            return data if data else await self.fetch_data(client, path, params)


class YearlyDataLoader(OpenDataLoader):
    async def fetch_total_record_count(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict,
    ) -> int:
        params[self._api_config.request_page] = 1
        params[self._api_config.request_size] = 1

        try:
            data = await self.fetch_data(client, path, params)
            return data[path][0]["head"][0]["list_total_count"]
        except (KeyError, IndexError, ValueError, TypeError):
            return 0

    async def fetch_paginated_data(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict | None = None,
        semaphore: asyncio.Semaphore = None,
    ) -> list[dict]:
        params = {} if params is None else params
        total_count = await self.fetch_total_record_count(client, path, params)

        if not total_count:
            return []

        params[self._api_config.request_size] = self._batch_size

        async def fetch(page):
            async with semaphore if semaphore else asyncio.Semaphore(self._concurrency_limit):
                params[self._api_config.request_page] = page
                response = await self.fetch_data(client, path, params)
                return response[path][1]["row"]

        tasks = [fetch(page) for page in range(1, ceil(total_count / self._batch_size) + 1)]
        data = list(chain.from_iterable(await asyncio.gather(*tasks)))

        return data

    async def get_data(self, path: str, params: dict | None = None) -> dict | list[dict]:
        if self.swagger_url:
            docs = await self.get_docs()
            self.apply_docs(docs)

        params = {} if params is None else params
        semaphore = asyncio.Semaphore(self._concurrency_limit)

        async with self.get_client() as client:

            async def fetch(year):
                params[self._api_config.request_year] = year
                return await self.fetch_paginated_data(client, path, params, semaphore)

            tasks = [fetch(year) for year in range(datetime.now().year - 30, datetime.now().year + 2)]
            data = list(chain.from_iterable(await asyncio.gather(*tasks)))

        return data
