from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.dependencies.db import Postgres, Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app start

    yield

    # app shutdown
    await Postgres.aclose()
    await Redis.aclose()
    print("Application Stopped")
