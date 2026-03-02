import redis
import json
import hashlib
import logging
from functools import wraps
from config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self._hits = 0
        self._misses = 0

    def get(self, key: str):
        value = self.client.get(key)
        if value:
            self._hits += 1
            logger.info(f"Cache hit for {key}")
            return json.loads(value)
        self._misses += 1
        logger.info(f"Cache miss for {key} — fetching from chain")
        return None

    def set(self, key: str, value: dict, ttl: int):
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key: str):
        self.client.delete(key)

    def delete_pattern(self, pattern: str):
        """Cache invalidation by pattern — e.g., 'portfolio:0xABC*'"""
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)
            logger.info(f"Cache cleared for pattern: {pattern} ({len(keys)} keys deleted)")

    def make_key(self, prefix: str, *args) -> str:
        """Create a consistent cache key from arguments"""
        raw = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(raw.encode()).hexdigest()[:16]

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return (self._hits / total * 100) if total > 0 else 0.0

cache = RedisCache()
