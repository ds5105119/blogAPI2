from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app start
    try:
        pass
    except Exception as e:
        raise e
    finally:
        yield

    # app shutdown
    print("Application Stopped")
