import redis
from fastapi import HTTPException, Request

from app.core.config import settings
from app.core.redis_client import redis_client


def rate_limit_shorten(request: Request):
    ip = request.client.host if request.client else "unknown"
    key = f"rate:shorten:{ip}"

    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, settings.rate_limit_window_seconds)
        ttl = redis_client.ttl(key)
    except redis.RedisError:
        return  

    if count > settings.rate_limit_requests:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(max(ttl, 1))},
        )