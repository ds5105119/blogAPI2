from fastapi import APIRouter, status

from webkit.throttle.decorator import limiter

router = APIRouter()


# 일반 유저의 경우
@limiter(20, 20)
@router.get("/", status_code=status.HTTP_200_OK)
async def abc():
    return {"ok": "아무응답"}


@limiter(10, 100)
@router.get("/new/", status_code=status.HTTP_200_OK)
@limiter(10, 100)
async def z():
    return {"이건 또 다른 api": "아무 출력"}
