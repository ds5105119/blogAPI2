from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", status_code=status.HTTP_200_OK)
async def test():
    return {"ok": "ok라구"}


test._limit_rules = 100
