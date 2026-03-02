import redis
import json
import os
from typing import Optional

class RedisCache:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")  # Render provides this automatically
        if redis_url:
            self.client = redis.from_url(redis_url, decode_responses=True)
        else:
            # Fallback for local dev
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True
            )
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[dict]:
        try:
            value = self.client.get(key)
            if value:
                self._hits += 1
                return json.loads(value)
            self._misses += 1
            return None
        except Exception:
            return None  # If Redis is down, fail gracefully

    def set(self, key: str, value: dict, ttl: int):
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass  # If Redis is down, still return data (just uncached)

    def delete_pattern(self, pattern: str):
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass

cache = RedisCache()
