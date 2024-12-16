import gzip
import json
from abc import ABC, abstractmethod

from webtool.cache import RedisCache


class BaseDataSaver(ABC):
    """
    REST API 의 데이터를 저장하고 불러오는 클래스

    Attributes:
        key_prefix (str): 키 전치사
        expire (int): 만료 (초)
    """

    key_prefix: str
    expire: int

    @abstractmethod
    async def get_cache(self, key: str) -> dict | None:
        """
        캐시로부터 데이터를 불러옵니다.

        Parameters:
            key (str): Cache Key
        """
        pass

    @abstractmethod
    async def set_cache(self, key: str, value: dict) -> None:
        """
        캐시에 대이터를 저장합니다.

        Parameters:
            key (str): Cache Key
            value (dict): Cache Value
        """
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
