from functools import wraps
from typing import Callable, Optional, Union

from fastapi import HTTPException, Request
from limiter import Limiter


class Limit:
    def __init__(self, limit: int, delay_seconds: float, identifier):
        self.limit = limit
        self._identifier = identifier

    def limiter(
        self,
        limit_value: Union[str, Callable[..., str]],
        identifier: Optional[Callable[..., str]] = None,
        per_method: bool = False,
        methods: Optional[list[str]] = None,
        error_message: Optional[str] = None,
        exempt_when: Optional[Callable[..., bool]] = None,
        cost: Union[int, Callable[..., int]] = 1,
        override_defaults: bool = True,
    ):
        def decorator(func):
            throttle_key = identifier or self._identifier
            func_name = f"{func.__module__}.{func.__name__}"

            @wraps(func)
            async def wrapper(*args, request: Request, **kwargs):
                user_id = request.client.host  # IP 기반, 또는 다른 식별자 사용

                if not await limiter.is_allowed(user_id):
                    remaining, ttl = await limiter.get_remaining_requests(user_id)
                    raise HTTPException(
                        status_code=429,
                        detail={"error": "Too Many Requests", "remaining": remaining, "reset_after": ttl},
                    )

                return await func(*args, request=request, **kwargs)

            return wrapper

        return decorator
