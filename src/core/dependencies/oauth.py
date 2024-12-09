from typing import Optional

from fastapi import Request
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer


class ExtendOAuth2PasswordBearer(OAuth2PasswordBearer):
    """
    Webtool 인증 미들웨어를 사용하는 Fastapi.security.OAuth2PasswordBearer
    """

    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


class ExtendOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    """
    Webtool 인증 미들웨어를 사용하는 Fastapi.security.OAuth2AuthorizationCodeBearer
    """

    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


oauth_password_schema = ExtendOAuth2PasswordBearer(tokenUrl="login")
