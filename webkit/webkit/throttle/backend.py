from abc import ABC, abstractmethod
from typing import Any, Callable, Literal, Optional, Tuple
from uuid import uuid4

from webkit.auth.service import BaseJWTService


def _get_header_value(header, name) -> Optional[str]:
    header = {key.decode("utf-8").lower(): val for key, val in header}
    val = header.get(name)

    if val is None:
        return val

    return val.decode("utf-8")


def _get_cookie_value(cookie: str, name) -> Optional[str]:
    cookie = dict(c.split("=") for c in cookie.split("; "))
    val = cookie.get(name)

    return val


class BaseBackend(ABC):
    @abstractmethod
    def authenticate(self, scope) -> Any | None:
        pass

    @staticmethod
    @abstractmethod
    def _callback():
        pass


class BaseAnnoBackend(BaseBackend):
    @abstractmethod
    def verify_identity(self, *args, **kwargs) -> Any:
        pass


class IPBackend(BaseBackend):
    def authenticate(self, scope) -> Any | None:
        client = scope.get("client")
        if client is None:
            return self._callback()

        return client[0]

    @staticmethod
    def _callback():
        return None


class SessionBackend(BaseBackend):
    def __init__(self, session_name: str):
        self.session_name = session_name

    def get_session(self, scope):
        headers = scope.get("headers")
        if headers is None:
            return False, None

        cookie = _get_header_value(headers, "cookie")
        if cookie is None:
            return False, None

        session = _get_cookie_value(cookie, self.session_name)
        if session is None:
            return False, None

        return True, session

    def authenticate(self, scope) -> Any | None:
        success, val = self.get_session(scope)
        if not success:
            return self._callback()

        return val

    @staticmethod
    def _callback():
        return None


class AnnoSessionBackend(SessionBackend, BaseAnnoBackend):
    def __init__(
        self,
        session_name,
        max_age: int = 1209600,
        secure: bool = True,
        same_site: Literal["lax", "strict", "none"] | None = "lax",
        session_factory: Optional[Callable] = uuid4,
    ):
        super().__init__(session_name)

        self.session_factory = session_factory
        self.security_flags = f"path=/; httponly; samesite={same_site}; Max-Age={max_age};"
        if secure:
            self.security_flags += f" secure;"

    async def verify_identity(self, scope, send):
        await send(
            {
                "type": "http.response.start",
                "status": 307,
                "headers": [
                    (b"location", scope["path"].encode()),
                    (
                        b"Set-Cookie",
                        f"{self.session_name}={self.session_factory().hex}; path=/; {self.security_flags}".encode(),
                    ),
                ],
            }
        )
        await send({"type": "http.response.body", "body": ""})


class JWTBackend(BaseBackend):
    def __init__(self, jwt_service: "BaseJWTService"):
        self.jwt_service = jwt_service

    @staticmethod
    def _get_authorization_scheme_param(
        authorization_header_value: Optional[str],
    ) -> Tuple[str, str]:
        if not authorization_header_value:
            return "", ""
        scheme, _, param = authorization_header_value.partition(" ")

        return scheme, param

    def get_token(self, scope):
        headers = scope.get("headers")
        if headers is None:
            return False, None

        authorization_value = _get_header_value(headers, "authorization")
        if authorization_value is None:
            return False, None

        scheme, param = self._get_authorization_scheme_param(authorization_value)
        if scheme.lower() != "bearer" or not param:
            return False, None

        return True, (scheme, param)

    def check_token(self, token):
        validated_token = self.jwt_service.check_access_token_expired(access_token=token)

        if validated_token is None:
            return False, None

        return True, validated_token

    def authenticate(self, scope) -> Any | None:
        success, val = self.get_token(scope)
        if not success:
            return self._callback()

        success, val = self.check_token(val[1])
        if not success:
            return self._callback()

        return val

    @staticmethod
    def _callback():
        return None
