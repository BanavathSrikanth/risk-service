import json


class RedisCache:
    def __init__(self, redis_url: str | None):
        self._client = None
        if redis_url:
            import redis

            self._client = redis.from_url(redis_url, decode_responses=True)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def get_json(self, key: str) -> dict | list | None:
        if not self._client:
            return None
        value = self._client.get(key)
        return json.loads(value) if value else None

    def set_json(self, key: str, value: dict | list, ttl_seconds: int = 300) -> None:
        if self._client:
            self._client.setex(key, ttl_seconds, json.dumps(value, default=str))
