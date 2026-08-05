from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.database import get_session
from src.auth_service.repositories.user_repository import UserRepository
from src.auth_service.services.auth_service import AuthService


def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    """Создаёт AuthService для обработки HTTP-запроса."""

    user_repository = UserRepository(session)

    return AuthService(
        session=session,
        user_repository=user_repository,
    )