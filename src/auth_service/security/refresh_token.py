import hashlib
import secrets
import uuid


class InvalidRefreshTokenFormatError(Exception):
    """Refresh token имеет некорректный формат."""


def generate_refresh_token() -> tuple[str, str]:
    """
    Создаёт refresh token.

    Returns:
        tuple:
            session_id — ID сессии в Redis
            refresh_token — токен, который отдаём клиенту
    """
    session_id = str(uuid.uuid4())
    secret = secrets.token_urlsafe(64)

    refresh_token = f"{session_id}.{secret}"

    return session_id, refresh_token


def get_session_id(refresh_token: str) -> str:
    """
    Получает session_id из refresh token.
    """
    session_id, separator, secret = refresh_token.partition(".")

    if not separator or not secret:
        raise InvalidRefreshTokenFormatError()

    try:
        uuid.UUID(session_id)
    except ValueError as error:
        raise InvalidRefreshTokenFormatError() from error

    return session_id


def hash_refresh_token(token: str) -> str:
    """
    Хеширует refresh token.

    В Redis храним не сам token, а только SHA-256.
    """
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()
