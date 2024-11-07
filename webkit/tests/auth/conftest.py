import pytest_asyncio

from app.core.config import settings
from webkit.auth import JWTService
from webkit.cache import RedisClient


@pytest_asyncio.fixture(scope="session")
async def jwt_service():
    client = RedisClient(settings.REDIS_DSN.unicode_string())
    service = JWTService(client, secret_key="test")

    try:
        yield service
    finally:
        await client.aclose()
