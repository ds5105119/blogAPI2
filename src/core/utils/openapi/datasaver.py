import gzip
import json
from abc import ABC, abstractmethod

from webtool.cache import RedisCache


class BaseDataSaver(ABC):
    key_prefix: str
    expire: int

    @abstractmethod
    async def get_cache(self, key: str) -> dict | None:
        pass

    @abstractmethod
    async def set_cache(self, key: str, value: dict) -> None:
        pass


class RedisDataSaver(BaseDataSaver):
    def __init__(self, cache: RedisCache, expire: int = 31536000, key_prefix: str = ""):
        self.expire = expire
        self.key_prefix = key_prefix
        self.cache = cache

    def get_cache_key(self, key: str | None) -> str:
        return f"{self.key_prefix}{key if key else ''}"

    async def get_cache(self, key: str) -> dict | None:
        cache_key = self.get_cache_key(key)
        serialized_data = await self.cache.get(cache_key)

        if serialized_data:
            return json.loads(gzip.decompress(serialized_data))
        return None

    async def set_cache(self, key: str, value: dict) -> None:
        cache_key = self.get_cache_key(key)

        serialized_data = gzip.compress(json.dumps(value).encode())
        await self.cache.set(cache_key, serialized_data, ex=self.expire)
