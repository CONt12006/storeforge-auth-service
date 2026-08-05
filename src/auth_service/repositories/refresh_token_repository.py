import json

from redis.asyncio import Redis


class RefreshTokenRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def save(
        self,
        session_id: str,
        user_id: int,
        token_hash: str,
        created_at: str,
        ttl_seconds: int,
    ) -> None:
        key = f"auth:refresh:{session_id}"

        value = {
            "user_id": user_id,
            "token_hash": token_hash,
            "created_at": created_at,
        }

        await self.redis.set(
            key,
            json.dumps(value),
            ex=ttl_seconds,
        )

    async def get(self, session_id: str) -> dict | None:
        value = await self.redis.get(
            f"auth:refresh:{session_id}"
        )

        if value is None:
            return None

        return json.loads(value)

    async def delete(self, session_id: str) -> None:
        await self.redis.delete(
            f"auth:refresh:{session_id}"
        )