from app.core.config import settings
from app.db import AsyncDB  # DB 불러오기
from webkit.auth import JWTService  # JWT 서비스 불러오기
from webkit.cache import RedisClient  # Redis client 불러오기
from webkit.throttle.backend import JWTBackend  # 인증 백엔드 불러오기

postgres = AsyncDB(settings.POSTGRES_DSN.unicode_string())  # postgres에 연결
redis_client = RedisClient(settings.REDIS_DSN.unicode_string())  # Redis에 연결
redis_client_2 = RedisClient(connection_pool=redis_client.connection_pool)  # 기존 redis에 연결된 것을 참조하여 연결
jwt_service = JWTService(redis_client, secret_key=settings.SECRET_KEY)  # Jwt 서비스 만들기
jwt_backend = JWTBackend(jwt_service)  # 서비스를 백엔드에 주입하기


print(jwt_service.create_access_token({"sub": "1"}))  # 만든 서비스로 엑세스 토큰 생성하기
