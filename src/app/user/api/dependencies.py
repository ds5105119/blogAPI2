from src.app.user.model.user import User
from src.app.user.repository.user import UserRepository
from src.app.user.service.user import UserService
from src.core.dependencies.auth import jwt_service

user_repository = UserRepository(User)
user_service = UserService(user_repository, jwt_service)
