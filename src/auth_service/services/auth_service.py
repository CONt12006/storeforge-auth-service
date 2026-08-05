from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.models import Users
from auth_service.repositories.user_repository import UserRepository
from auth_service.schemas.auth import RegisterRequest
from auth_service.security.password import hash_password


class EmailAlreadyExistsError(Exception):
    """Ошибка: пользователь с таким email уже существует."""


class AuthService:
    """Сервис бизнес-логики регистрации и авторизации."""

    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        """
        Инициализирует сервис аутентификации.

        Args:
            session: Сессия для управления транзакцией.
            user_repository: Репозиторий пользователей.
        """
        self.session = session
        self.user_repository = user_repository

    async def register(self, request: RegisterRequest) -> Users:
        """
        Регистрирует нового пользователя.

        Проверяет уникальность email, хеширует пароль, создаёт пользователя
        и фиксирует изменения в базе данных.

        Args:
            request: Данные регистрации.

        Returns:
            Созданный пользователь.

        Raises:
            EmailAlreadyExistsError: Если email уже занят.
        """
        existing_user = await self.user_repository.get_by_email(
            request.email,
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError()

        password_hash = hash_password(request.password)

        user = await self.user_repository.create(
            email=request.email,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        await self.session.commit()

        return user