from typing import Optional

from fastapi import Request
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer


class ExtendOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


class ExtendOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth
