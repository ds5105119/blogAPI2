from typing import Callable, Iterable, Optional

from starlette.routing import BaseRoute, Match

from webkit.throttle.backend import AnnoSessionBackend, BaseAnnoBackend, BaseBackend
from webkit.throttle.decorator import THROTTLE_RULE_ATTR_NAME, Limit, LimitRule, find_closure_rules_function
from webkit.throttle.limiter import Limiter


def _find_route_handler(routes: Iterable[BaseRoute], scope) -> Optional[Callable]:
    """
    Finds and returns the route handler function for the given scope.

    :param routes: Iterable of BaseRoute objects
    :param scope: ASGI request scope
    :return: Route handler function or None if not found
    """

    for route in routes:
        match, _ = route.matches(scope)
        if match == Match.FULL and hasattr(route, "endpoint"):
            return route.endpoint
    return None


async def _default_callback(scope, send, expire: int):
    """
    Default callback function for rate limit exceeded response.
    Returns a 429 status code with Retry-After header.

    :param scope: ASGI request scope
    :param send: ASGI send function
    :param expire: Time until rate limit reset (in seconds)
    """

    await send(
        {
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"location", scope["path"].encode()),
                (b"Retry-After", str(expire).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": ""})


class LimitMiddleware:
    """
    Middleware for implementing rate limiting in ASGI applications.

    This middleware supports both authenticated and anonymous users,
    applying rate limits based on user identifiers or session IDs.
    """

    def __init__(
        self,
        app,
        redis,
        auth_backend: "BaseBackend",
        anno_backend: "BaseAnnoBackend" = None,
    ) -> None:
        """
        :param app: ASGI application
        :param redis: Redis client instance for storing rate limit data
        :param auth_backend: Authentication backend for identifying users
        :param anno_backend: Backend for handling anonymous users (defaults to AnnoSessionBackend)
        """

        self.app = app
        self.limiter = Limiter(redis)
        self.limit = None
        self.auth_backend = auth_backend
        self.anno_backend = anno_backend or AnnoSessionBackend("th-session")

    async def __call__(self, scope, receive, send):
        """
        Main middleware handler that processes each request.

        :param scope: ASGI request scope
        :param receive: ASGI receive function
        :param send: ASGI send function
        """

        # http check
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # find handler
        routes = scope["app"].routes
        handler = _find_route_handler(routes, scope)
        if handler is None:
            return await self.app(scope, receive, send)

        # find limit
        handler = find_closure_rules_function(handler)
        limit: Limit = getattr(handler, THROTTLE_RULE_ATTR_NAME)

        # auth check
        user_auth = self.auth_backend.authenticate(scope)
        if user_auth is not None:
            user_id = self.auth_backend.get_identifier(user_auth)
            rules = limit.should_limit(scope, user_identifier=user_id)
            return await self.apply(scope, receive, send, rules, user_id)

        # anno check
        anno_auth = self.anno_backend.authenticate(scope)
        if anno_auth is not None:
            anno_id = self.anno_backend.get_identifier(anno_auth)
            rules = limit.should_limit(scope, user_identifier=anno_id)
            return await self.apply(scope, receive, send, rules, anno_id)

        # issue limit identifier
        return await self.anno_backend.verify_identity(scope, send)

    async def apply(self, scope, receive, send, rules: list["LimitRule"], identifier):
        """
        Applies rate limiting rules and handles the request.

        :param scope: ASGI request scope
        :param receive: ASGI receive function
        :param send: ASGI send function
        :param rules: List of LimitRule objects to apply
        :param identifier: User or session identifier for rate limiting
        :return: Response from app or rate limit exceeded response
        """

        if rules:
            deny = await self.limiter.is_deny(identifier, rules)
            if deny:
                return await _default_callback(scope, send, int(max(deny)))

        return await self.app(scope, receive, send)
