import asyncio
from typing import TypedDict

import msgspec
from redis.asyncio.client import Redis


class Rule(TypedDict):
    key: str
    limit: int
    window_size: int


class Limiter:
    LUA_SCRIPT = """
    -- Retrieve arguments
    -- ruleset = {key: [limit, window_size], ...}
    -- return = {key: [limit, current], ...}
    local now = tonumber(ARGV[1])
    local ruleset = cjson.decode(ARGV[2])

    for i, key in ipairs(KEYS) do
        -- Step 1: Remove expired requests from the sorted set
        redis.call('ZREMRANGEBYSCORE', key, 0, now - ruleset[key][2])

        -- Step 2: Count the number of requests within the valid time window
        local amount = redis.call('ZCARD', key)

        -- Step 3: Add the current request timestamp to the sorted set
        if amount < ruleset[key][1] then
            redis.call('ZADD', key, now, tostring(now))
            amount = amount + 1
        end

        -- Step 4: Set the TTL for the key
        redis.call("EXPIRE", key, ruleset[key][2])
        ruleset[key][2] = amount
    end

    return cjson.encode(ruleset)
    """

    def __init__(self, redis: Redis):
        self._redis = redis
        self._redis_function = self._redis.register_script(Limiter.LUA_SCRIPT)

    @staticmethod
    def _get_ruleset(identifier: str, rules: list[Rule]) -> dict[str, tuple[int, int]]:
        keys = map(lambda rule: identifier + rule.pop("key"), rules)
        args = map(lambda rule: tuple(rule.values()), rules)

        return dict(zip(keys, args))

    async def _get_limits(self, ruleset) -> dict[str, list[int, int]]:
        now = asyncio.get_running_loop().time()

        result = await self._redis_function(keys=list(ruleset.keys()), args=[now, msgspec.json.encode(ruleset)])
        result = msgspec.json.decode(result)

        return result

    async def is_allowed(self, identifier: str, rules: list[Rule]) -> bool:
        ruleset = self._get_ruleset(identifier, rules)

        result = await self._get_limits(ruleset)
        allowed = not any([v[0] <= v[1] for v in result.values()])

        return allowed


from app.core.config import settings
from webkit.cache import RedisClient


async def main():
    client = RedisClient(settings.REDIS_DSN)
    limiter = Limiter(client.redis)
    rule1 = Rule(key="a", limit=10, window_size=10)
    rule2 = Rule(key="b", limit=5, window_size=10)

    result = await limiter.is_allowed("a", rules=[rule1, rule2])
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
