from typing import Callable
from fastapi import FastAPI

from app.db.session import SessionLocal


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        # 데이터베이스 연결 테스트
        db = SessionLocal()
        try:
            # 간단한 쿼리로 연결 테스트
            db.execute("SELECT 1")
        except Exception as e:
            print(f"DB Connection Failed: {e}")
            raise e
        finally:
            db.close()

        print("Application Started")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    @app.on_event("shutdown")
    async def stop_app() -> None:
        # 애플리케이션 종료 시 수행할 작업
        print("Application Stopped")

    return stop_app
