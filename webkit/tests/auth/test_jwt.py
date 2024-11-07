import asyncio
import time

import pytest
import pytest_asyncio

from app.core.config import settings
from webkit.auth import JWTService
from webkit.cache import RedisClient


@pytest_asyncio.fixture(scope="session")
async def jwt_service():
    client = RedisClient(settings.REDIS_DSN)
    service = JWTService(client, secret_key="test")

    try:
        yield service
    finally:
        await client.aclose()


@pytest.mark.asyncio(scope="session")
async def test_create_access_token(jwt_service):
    token_data = {"sub": "user123"}
    access_token = jwt_service.create_access_token(token_data)
    assert access_token


@pytest.mark.asyncio(scope="session")
async def test_create_refresh_token(jwt_service):
    token_data = {"sub": "user123"}
    access_token = jwt_service.create_access_token(token_data)
    refresh_token = await jwt_service.create_refresh_token(token_data, access_token)
    assert refresh_token


@pytest.mark.asyncio(scope="session")
async def test_update_token(jwt_service):
    token_data = {"sub": "user123"}

    access_token = jwt_service.create_access_token(token_data)
    refresh_token = await jwt_service.create_refresh_token(token_data, access_token)

    new_access_token, new_refresh_token = await jwt_service.update_token(token_data, access_token, refresh_token)
    time.sleep(1)

    try:
        _ = await jwt_service.update_token(token_data, access_token, refresh_token)
    except ValueError:
        pass
    else:
        assert True, "유효하지 않은 토큰으로 리프레시 성공"
