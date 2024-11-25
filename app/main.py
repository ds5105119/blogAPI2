from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from webtool.throttle import LimitMiddleware

from app.api.v1.api import router
from app.core.config import settings
from app.core.lifespan import lifespan
from app.dependencies.db import Redis
from app.dependencies.services import jwt_backend


def create_application(dev=False) -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,  # type: ignore
            allow_origins=settings.cors_allow_origin if not dev else ["*"],
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
            cache=Redis,
            auth_backend=jwt_backend,
        ),
    ]

    application = FastAPI(
        title=settings.project_name,
        docs_url=f"{settings.swagger_url}/docs",
        redoc_url=f"{settings.swagger_url}/redoc",
        openapi_url=f"{settings.swagger_url}/openapi.json",
        version="1.0.0",
        lifespan=lifespan,
        middleware=middleware,
        default_response_class=ORJSONResponse,
    )

    application.include_router(router, prefix=settings.api_url)

    return application


app = create_application(dev=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
