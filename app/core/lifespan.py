from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app start
    try:
        print("앱 실행")
    except Exception as e:
        print(f"DB Connection Failed: {e}")
        raise e

    yield

    # app shutdown
    print("Application Stopped")
