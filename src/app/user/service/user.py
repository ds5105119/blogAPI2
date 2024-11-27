from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession as Session

from src.app.user.model.user import User
from src.app.user.repository.user import UserRepository, user_repository
from src.app.user.schema.register import EmailDto, HandleDto, RegisterDto

T = TypeVar("T", bound=BaseModel)
EmailDtoT = TypeVar("EmailDtoT", bound=EmailDto)
HandleDtoT = TypeVar("HandleDtoT", bound=HandleDto)


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def _check_unique_user(self, data: RegisterDto, session: Session) -> T:
        user = await self.repository.get_by_where(
            session,
            columns=["email", "handle"],
            filters=[self.repository.model.email == data.email],
        )

        if user.all():
            raise ValueError(f"email {data.email} already exists")
        return data

    async def register_user(self, data: RegisterDto, session: Session) -> User:
        data = await self._check_unique_user(data, session)

        data = data.model_dump(by_alias=True)
        user = await self.repository.create(session, **data)

        return user

    @staticmethod
    def user_to_claim(user: User):
        return {
            "sub": user.id,
        }


user_service = UserService(user_repository)
