from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.database import get_session
from auth_service.repositories.user_repository import UserRepository
from auth_service.services.auth_service import AuthService


def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    """Создаёт AuthService для обработки HTTP-запроса."""

    user_repository = UserRepository(session)

    return AuthService(
        session=session,
        user_repository=user_repository,
    )