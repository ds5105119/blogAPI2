from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app import dependencies
from app.api.v1.api import router
from app.core.config import settings
from app.core.lifespan import lifespan
from webkit.throttle import LimitMiddleware
from webkit.utils import MsgSpecJSONResponse


def create_application() -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,  # type: ignore
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            LimitMiddleware,  # type: ignore
            redis=dependencies.redis_client.redis,
        ),
    ]

    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f"{settings.SWAGGER_URL}/docs",
        redoc_url=f"{settings.SWAGGER_URL}/redoc",
        openapi_url=f"{settings.SWAGGER_URL}/openapi.json",
        version="1.0.0",
        lifespan=lifespan,
        middleware=middleware,
        default_response_class=MsgSpecJSONResponse,
    )

    application.include_router(router, prefix=settings.API_URL)

    return application


# for dev
def create_dev_application() -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,  # type: ignore
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            ProxyHeadersMiddleware,  # type: ignore
            trusted_hosts=["*"],
        ),
        Middleware(
            LimitMiddleware,  # type: ignore
            redis=dependencies.redis_client.redis,
            auth_backend=dependencies.jwt_backend,
        ),
    ]

    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f"{settings.SWAGGER_URL}/docs",
        redoc_url=f"{settings.SWAGGER_URL}/redoc",
        openapi_url=f"{settings.SWAGGER_URL}/openapi.json",
        description="Development BlogAPI",
        version="0.0.1",
        lifespan=lifespan,
        middleware=middleware,
        default_response_class=MsgSpecJSONResponse,
    )

    application.include_router(router, prefix=settings.API_URL)

    return application


app = create_dev_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
