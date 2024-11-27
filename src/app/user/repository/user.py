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
    pass


class UserUpdateRepository(BaseUpdateRepository[User]):
    pass


class UserDeleteRepository(BaseDeleteRepository[User]):
    pass


class UserRepository(UserCreateRepository, UserReadRepository, UserUpdateRepository, UserDeleteRepository):
    pass


user_repository = UserRepository(User)
