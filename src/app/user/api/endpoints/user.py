from fastapi import APIRouter, Depends, Response, status
from webtool.throttle.decorator import limiter

from src.app.user.api.dependencies import ExtendOAuth2PasswordBearer
from src.app.user.schema.register import RegisterDto
from src.app.user.service.user import user_service
from src.core.dependencies.auth import jwt_service
from src.core.dependencies.db import db_session

router = APIRouter()
oauth_password_schema = ExtendOAuth2PasswordBearer(tokenUrl="login")


@router.get("/login", status_code=status.HTTP_200_OK)
async def get_token():
    tokens = await jwt_service.create_token({"sub": "123"})
    return tokens


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user(
    data: RegisterDto,
    session: db_session,
    response: Response,
):
    user = await user_service.register_user(data, session)
    claim = user_service.user_to_claim(user)
    access, refresh = await jwt_service.create_token(claim)
    response.set_cookie(key="refresh", value=refresh)

    return {"access": access, "refresh": refresh}


@limiter(10, 100)
@router.get("/new", status_code=status.HTTP_200_OK)
async def auth_info(auth=Depends(oauth_password_schema)):
    return {"auth_info 응답": auth}
