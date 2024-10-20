from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app start
    try:
        async for session in get_db():
            await session.execute(text("SELECT 1"))
    except Exception as e:
        print(f"DB Connection Failed: {e}")
        raise e

    yield

    # app shutdown
    print("Application Stopped")
