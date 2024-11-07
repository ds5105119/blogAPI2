import pytest

from app.core.config import settings
from webkit.auth import JWTService
from webkit.cache import RedisClient


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def jwt_service():
    client = RedisClient(settings.REDIS_DSN)
    service = JWTService(client, secret_key="test")
    return service
