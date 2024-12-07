from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.dependencies.db import Postgres, Redis
from src.core.dependencies.fiscal import fiscal_data_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app start
    await fiscal_data_manager.init()

    yield

    # app shutdown
    await Postgres.aclose()
    await Redis.aclose()
    print("Application Stopped")
