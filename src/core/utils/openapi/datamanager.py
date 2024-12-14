from abc import ABC, abstractmethod

import polars as pl

from .dataloader import BaseOpenDataLoader
from .datasaver import BaseDataSaver


class BaseDataManager(ABC):
    @abstractmethod
    async def init(self):
        pass


class PolarsDataManager(BaseDataManager):
    def __init__(
        self,
        data_loader: BaseOpenDataLoader,
        data_saver: BaseDataSaver,
        path: str,
        params: dict | None = None,
        infer_scheme_length: int = 100000,
    ):
        self.data_loader = data_loader
        self.data_saver = data_saver
        self.data = pl.DataFrame()
        self.path = path
        self.params = params or {}
        self._infer_scheme_length = infer_scheme_length

    async def init(self, reload: bool = False):
        if not reload:
            data = await self.data_saver.get_cache(self.path)
        else:
            data = None

        if data is None:
            data = await self.data_loader.get_data(self.path, self.params)
            await self.data_saver.set_cache(self.path, data)

        self.data = pl.DataFrame(data, infer_schema_length=self._infer_scheme_length)
