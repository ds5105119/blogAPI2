from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.dependencies.data import (
    fiscal_data_manager,
    gov24_service_conditions_manager,
    gov24_service_detail_manager,
    gov24_service_list_manager,
)
from src.core.dependencies.db import Postgres, Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app start
    print("Application Started")
    await fiscal_data_manager.init()
    await gov24_service_conditions_manager.init()
    await gov24_service_detail_manager.init()
    await gov24_service_list_manager.init()

    yield

    # app shutdown
    await Postgres.aclose()
    await Redis.aclose()
    print("Application Stopped")
