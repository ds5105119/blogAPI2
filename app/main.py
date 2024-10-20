from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.lifespan import lifespan


def get_application() -> FastAPI:
    middleware = Middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f"{settings.SWAGGER_URL}/docs",
        redoc_url=f"{settings.SWAGGER_URL}/redoc",
        openapi_url=f"{settings.SWAGGER_URL}/openapi.json",
        version="1.0.0",
        lifespan=lifespan,
        middleware=[middleware],
    )

    # 라우터 포함
    application.include_router(api_router, prefix=settings.API_URL)

    return application


# for dev
def get_dev_application() -> FastAPI:
    middleware = Middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f"{settings.SWAGGER_URL}/docs",
        redoc_url=f"{settings.SWAGGER_URL}/redoc",
        openapi_url=f"{settings.SWAGGER_URL}/openapi.json",
        description="Development BlogAPI",
        version="0.0.1",
        lifespan=lifespan,
        middleware=[middleware],
    )

    # 라우터 포함
    application.include_router(api_router, prefix=settings.API_URL)

    return application


app = get_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_dev_application(), host="0.0.0.0", port=8000)
