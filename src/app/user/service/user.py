import argon2
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession as Session
from webtool.auth import JWTService

from src.app.user.repository.user import UserRepository, user_repository
from src.app.user.schema import login, register
from src.core.dependencies.auth import jwt_service
from src.core.dependencies.auth import jwt_service as default_jwt_service


class UserService:
    def __init__(self, repository: UserRepository, jwt_service: JWTService):
        self.repository = repository
        self.jwt_service = jwt_service
        self.password_hasher = argon2.PasswordHasher()

    @staticmethod
    def _user_to_claim(user):
        return {
            "sub": user.id,
        }

    async def _issue_tokens(self, db_user):
        payload = self._user_to_claim(db_user)
        return await jwt_service.create_token(payload)

    async def _is_register_valid(self, data: register.RegisterDto, session: Session):
        user = await self.repository.get_unique_fields(session, data.email, data.handle)

        if user.all():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"email {data.email} already exists",
            )

        return user

    async def _is_login_valid(self, data: login.LoginDto, session: Session):
        if data.email:
            user = await self.repository.get_user_by_email(session, data.email)
        else:
            user = await self.repository.get_user_by_handle(session, data.handle)

        user = user.mappings().first()

        try:
            self.password_hasher.verify(user.password, data.password)
        except (argon2.exceptions.Argon2Error, AttributeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Can not find user",
            )

        return user

    async def register_user(self, data: register.RegisterDto, session: Session):
        user = await self._is_register_valid(data, session)

        data = data.model_dump(by_alias=True)
        data["password"] = self.password_hasher.hash(data["password"])
        user = await self.repository.create(session, **data)

        access, refresh = await self._issue_tokens(user)
        return access, refresh

    async def login_user(self, data: login.LoginDto, session: Session):
        user = await self._is_login_valid(data, session)

        access, refresh = await self._issue_tokens(user)
        return access, refresh


user_service = UserService(user_repository, default_jwt_service)
