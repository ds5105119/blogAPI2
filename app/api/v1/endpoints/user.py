from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from webtool.throttle.decorator import limiter

from app.dependencies.services import jwt_service

router = APIRouter()


class ExtendOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


class ExtendOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


oauth_password_schema = ExtendOAuth2PasswordBearer(tokenUrl="api/v1/token")


@router.get("/token/", status_code=status.HTTP_200_OK)
async def get_token():
    tokens = await jwt_service.create_token({"sub": "123"})

    return tokens


# 유저에게만 스로틀을 걸기
@limiter(10, 100)
@router.get("/new/", status_code=status.HTTP_200_OK)
async def auth_info(auth=Depends(oauth_password_schema)):
    return {"auth_info 응답": auth}
