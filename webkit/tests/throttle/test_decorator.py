import pytest

from webkit.throttle.decorator import THROTTLE_RULE_ATTR_NAME, find_closure_rules_function, limiter


def test_decorator():
    x = 0

    def decorator(func):
        c = x

        def wrapper(*args, **kwargs):
            print(c)
            return func(*args, **kwargs)

        return wrapper

    @decorator
    @decorator
    @decorator
    @decorator
    @limiter(100, 10, "z")
    @decorator
    @limiter(100, 20, "abc")
    @decorator
    @decorator
    @decorator
    @decorator
    @limiter(100, 30, "bab")
    @decorator
    @decorator
    @decorator
    def x():
        print("abc")

    rules = list(getattr(find_closure_rules_function(x), THROTTLE_RULE_ATTR_NAME).rules)
    print(rules)
    assert "100 per 30 bab [] []" in rules.__repr__(), "매치 실패"
    assert "100 per 20 abc [] []" in rules.__repr__(), "매치 실패"
    assert "100 per 10 z [] []" in rules.__repr__(), "매치 실패"
