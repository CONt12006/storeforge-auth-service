from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.database import get_session
from auth_service.database.models import User
from auth_service.repositories.role_repository import RoleRepository
from auth_service.repositories.user_repository import UserRepository
from auth_service.security.jwt import (
    InvalidTokenError,
    decode_access_token,
)
from auth_service.services.auth_service import AuthService


bearer_scheme = HTTPBearer()


def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    """
    Создаёт AuthService для обработки HTTP-запроса.

    FastAPI получает SQLAlchemy-сессию через get_session(),
    затем создаёт репозитории пользователей и ролей и передаёт
    их в AuthService.

    Args:
        session: Асинхронная SQLAlchemy-сессия.

    Returns:
        Готовый объект AuthService.
    """
    user_repository = UserRepository(session)
    role_repository = RoleRepository(session)

    return AuthService(
        session=session,
        user_repository=user_repository,
        role_repository=role_repository,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Проверяет JWT и возвращает текущего пользователя.

    Метод:

    1. Получает JWT из заголовка Authorization.
    2. Проверяет подпись и срок действия JWT.
    3. Извлекает ID пользователя из поля sub.
    4. Находит пользователя в PostgreSQL.
    5. Проверяет, что пользователь активен.

    Args:
        credentials: Данные из заголовка Authorization.
        session: Асинхронная SQLAlchemy-сессия.

    Returns:
        Пользователь, которому принадлежит JWT.

    Raises:
        HTTPException:
            Если токен недействителен или просрочен.
        HTTPException:
            Если пользователь не найден.
        HTTPException:
            Если пользователь заблокирован.
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])

    except (
        InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    user_repository = UserRepository(session)

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь заблокирован",
        )

    return user