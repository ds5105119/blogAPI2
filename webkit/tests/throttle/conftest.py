import pytest
import pytest_asyncio

from app.core.config import settings
from webkit.auth import JWTService
from webkit.cache import RedisClient
from webkit.throttle.limiter import Limiter


@pytest_asyncio.fixture(scope="session")
async def redis():
    client = RedisClient(settings.REDIS_DSN.unicode_string())

    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture(scope="session")
async def jwt_service(redis):
    service = JWTService(redis, secret_key="test")

    try:
        yield service
    finally:
        await redis.aclose()


@pytest_asyncio.fixture(scope="session")
async def limiter(redis):
    limiter = Limiter(redis.redis)

    try:
        yield limiter
    finally:
        await redis.aclose()
