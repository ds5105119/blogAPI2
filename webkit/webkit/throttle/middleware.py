from typing import Callable, Iterable, Literal, Optional

from starlette.routing import BaseRoute, Match
from starlette.types import Scope

from webkit.throttle.backend import AnnoSessionBackend, BaseAnnoBackend, BaseBackend
from webkit.throttle.limiter import Limiter, Rule


def _find_route_handler(routes: Iterable[BaseRoute], scope: Scope) -> Optional[Callable]:
    for route in routes:
        match, _ = route.matches(scope)
        if match == Match.FULL and hasattr(route, "endpoint"):
            return route.endpoint
    return None


class LimitMiddleware:
    def __init__(
        self,
        app,
        redis,
        auth_backend: "BaseBackend",
        anno_backend: "BaseAnnoBackend" = None,
    ) -> None:
        self.app = app
        self.limiter = Limiter(redis)
        self.limit = None
        self.auth_backend = auth_backend
        self.anno_backend = anno_backend or AnnoSessionBackend("th-session")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        routes = scope["app"].routes
        handler = _find_route_handler(routes, scope)
        if handler is None:
            return await self.app(scope, receive, send)

        rules = self._get_limit_rules(handler)

        auth = self.auth_backend.authenticate(scope)
        if auth is not None:
            return await self.app(scope, receive, send)

        anno = self.anno_backend.authenticate(scope)
        if anno is not None:
            return await self.app(scope, receive, send)

        return await self.anno_backend.verify_identity(scope, send)

    @staticmethod
    def _get_limit_rules(handler: Callable) -> Iterable[Rule] | None:
        return getattr(handler, "_limit_rules", None)
