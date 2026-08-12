import json

from redis.asyncio import Redis


class RefreshTokenRepository:
    """Хранилище refresh-сессий в Redis."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f"auth:refresh:{session_id}"

    @staticmethod
    def _user_sessions_key(user_id: int) -> str:
        return f"auth:user_sessions:{user_id}"

    async def save(
        self,
        *,
        session_id: str,
        user_id: int,
        token_hash: str,
        created_at: str,
        ttl_seconds: int,
    ) -> None:
        value = {
            "user_id": user_id,
            "token_hash": token_hash,
            "created_at": created_at,
        }

        pipeline = self.redis.pipeline(
            transaction=True
        )

        pipeline.set(
            self._session_key(session_id),
            json.dumps(value),
            ex=ttl_seconds,
        )

        pipeline.sadd(
            self._user_sessions_key(user_id),
            session_id,
        )

        pipeline.expire(
            self._user_sessions_key(user_id),
            ttl_seconds,
        )

        await pipeline.execute()

    async def get(
        self,
        session_id: str,
    ) -> dict | None:
        value = await self.redis.get(
            self._session_key(session_id)
        )

        if value is None:
            return None

        return json.loads(value)

    async def delete(
        self,
        session_id: str,
    ) -> None:
        session = await self.get(session_id)

        if session is None:
            return

        user_id = int(session["user_id"])

        pipeline = self.redis.pipeline(
            transaction=True
        )

        pipeline.delete(
            self._session_key(session_id)
        )

        pipeline.srem(
            self._user_sessions_key(user_id),
            session_id,
        )

        await pipeline.execute()

    async def delete_all_for_user(
        self,
        user_id: int,
    ) -> None:
        sessions_key = self._user_sessions_key(
            user_id
        )

        session_ids = await self.redis.smembers(
            sessions_key
        )

        pipeline = self.redis.pipeline(
            transaction=True
        )

        for session_id in session_ids:
            pipeline.delete(
                self._session_key(session_id)
            )

        pipeline.delete(sessions_key)

        await pipeline.execute()
