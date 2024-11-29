from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from webtool.throttle import LimitMiddleware

from src.app.router import router
from src.core.config import settings
from src.core.dependencies.auth import jwt_backend
from src.core.dependencies.db import Redis
from src.core.lifespan import lifespan


def create_application(debug=False) -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,  # type: ignore
            allow_origins=settings.cors_allow_origin if not debug else ["*"],
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


app = create_application(debug=settings.debug)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
