from fastapi import APIRouter

from app.api.v1.endpoints import user

router = APIRouter()

router.include_router(user.router, prefix="/user", tags=["user"])
