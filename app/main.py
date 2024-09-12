from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_STR}/openapi.json",
        version="1.0.0"
    )

    # CORS middleware의 IDE type error는 무시할 수 있음.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 포함
    application.include_router(api_router, prefix=settings.API_STR)

    # 시작 및 종료 이벤트 핸들러 설정
    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    return application


# for dev
def get_dev_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_STR}/openapi.json",
        description="Development BlogAPI",
        version="0.0.1"
    )

    # CORS 설정
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 포함
    application.include_router(api_router, prefix=settings.API_STR)

    # 시작 및 종료 이벤트 핸들러 설정
    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    return application


app = get_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(get_dev_application(), host="0.0.0.0", port=8000)
