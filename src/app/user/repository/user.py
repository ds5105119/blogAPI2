from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession as Session

from src.app.user.model.user import User
from src.core.models.repository import (
    BaseCreateRepository,
    BaseDeleteRepository,
    BaseReadRepository,
    BaseUpdateRepository,
)


class UserCreateRepository(BaseCreateRepository[User]):
    pass


class UserReadRepository(BaseReadRepository[User]):
    async def get_unique_fields(self, session: Session, email: str, handle: str):
        result = await self.get(
            session,
            columns=["email", "handle"],
            filters=[
                or_(
                    self.model.email == email,
                    self.model.handle == handle,
                ),
            ],
        )
        return result

    async def get_user_by_email(self, session: Session, email: str):
        result = await self.get(session, columns=["id", "password"], filters=[self.model.email == email])
        return result

    async def get_user_by_handle(self, session: Session, handle: str):
        result = await self.get(session, columns=["id", "password"], filters=[self.model.handle == handle])
        return result


class UserUpdateRepository(BaseUpdateRepository[User]):
    pass


class UserDeleteRepository(BaseDeleteRepository[User]):
    pass


class UserRepository(UserCreateRepository, UserReadRepository, UserUpdateRepository, UserDeleteRepository):
    pass


user_repository = UserRepository(User)
