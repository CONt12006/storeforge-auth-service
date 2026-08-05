from datetime import datetime, timedelta, timezone

from jose import jwt

from auth_service.config import settings


def create_access_token(
    *,
    user_id: int,
    roles: list[str],
) -> str:
    """
    Создаёт JWT access token пользователя.

    Args:
        user_id: ID пользователя в PostgreSQL.
        roles: Названия ролей пользователя.

    Returns:
        Подписанный JWT в виде строки.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    payload = {
        "sub": str(user_id),
        "roles": roles,
        "type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )