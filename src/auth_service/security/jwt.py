from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from auth_service.config import settings


class InvalidTokenError(Exception):
    """Ошибка: JWT недействителен или просрочен."""


def create_access_token(
    *,
    user_id: int,
    roles: list[str],
) -> str:
    """
    Создаёт JWT access token пользователя.

    Args:
        user_id: ID пользователя.
        roles: Роли пользователя.

    Returns:
        Подписанный JWT.
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


def decode_access_token(token: str) -> dict:
    """
    Проверяет JWT и возвращает его содержимое.

    Args:
        token: JWT из заголовка Authorization.

    Returns:
        Данные, записанные внутри токена.

    Raises:
        InvalidTokenError:
            Если подпись неверна, токен просрочен
            или имеет неправильный тип.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as error:
        raise InvalidTokenError() from error

    if payload.get("type") != "access":
        raise InvalidTokenError()

    if payload.get("sub") is None:
        raise InvalidTokenError()

    return payload