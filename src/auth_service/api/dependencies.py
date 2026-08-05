from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.database import get_session
from auth_service.repositories.user_repository import UserRepository
from auth_service.services.auth_service import AuthService
from auth_service.repositories.role_repository import RoleRepository


def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    """Создаёт AuthService для обработки HTTP-запроса."""

    user_repository = UserRepository(session)
    role_repository = RoleRepository(session)

    return AuthService(
        session=session,
        user_repository=user_repository,
        role_repository=role_repository,
    )