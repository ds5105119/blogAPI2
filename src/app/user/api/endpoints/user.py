from fastapi import APIRouter, Response, status

from src.app.user.api.dependencies import ExtendOAuth2PasswordBearer
from src.app.user.schema.login import LoginDto, LoginResponse
from src.app.user.schema.register import RegisterDto, RegisterResponse
from src.app.user.service.user import user_service
from src.core.dependencies.db import db_session

router = APIRouter()
oauth_password_schema = ExtendOAuth2PasswordBearer(tokenUrl="login")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: LoginDto, session: db_session, response: Response):
    access, refresh = await user_service.login_user(data, session)
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return LoginResponse(access=access)


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(data: RegisterDto, session: db_session, response: Response):
    access, refresh = await user_service.register_user(data, session)
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return RegisterResponse(access=access)
