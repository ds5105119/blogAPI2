from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from src.app.user.api.dependencies import ExtendOAuth2PasswordBearer
from src.app.user.schema.login import LoginResponse
from src.app.user.schema.register import RegisterResponse
from src.app.user.service.user import user_service

router = APIRouter()
oauth_password_schema = ExtendOAuth2PasswordBearer(tokenUrl="login")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(tokens: Annotated[tuple[str, str], Depends(user_service.login_user)], response: Response):
    access, refresh = tokens
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return LoginResponse(access=access)


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(tokens: Annotated[tuple[str, str], Depends(user_service.register_user)], response: Response):
    access, refresh = tokens
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return RegisterResponse(access=access)
