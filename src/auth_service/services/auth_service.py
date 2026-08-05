from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.models import User
from auth_service.repositories.role_repository import RoleRepository
from auth_service.repositories.user_repository import UserRepository
from auth_service.schemas.auth import LoginRequest, RegisterRequest
from auth_service.security.jwt import create_access_token
from auth_service.security.password import hash_password, verify_password


class EmailAlreadyExistsError(Exception):
    """Ошибка: пользователь с таким email уже существует."""


class InvalidCredentialsError(Exception):
    """Ошибка: email или пароль указаны неверно."""


class UserInactiveError(Exception):
    """Ошибка: пользователь заблокирован."""


class AuthService:
    """Сервис регистрации и авторизации пользователей."""

    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        """
        Инициализирует сервис аутентификации.

        Args:
            session: Асинхронная SQLAlchemy-сессия для управления транзакцией.
            user_repository: Репозиторий для работы с пользователями.
            role_repository: Репозиторий для работы с ролями.
        """
        self.session = session
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def register(self, request: RegisterRequest) -> User:
        """
        Регистрирует нового пользователя и назначает ему роль customer.

        Метод:

        1. Проверяет, что email ещё не занят.
        2. Хеширует пароль.
        3. Создаёт пользователя.
        4. Находит или создаёт роль customer.
        5. Назначает роль пользователю.
        6. Фиксирует транзакцию.

        Args:
            request: Проверенные данные регистрации пользователя.

        Returns:
            Созданный пользователь.

        Raises:
            EmailAlreadyExistsError: Если пользователь с таким email уже есть.
        """
        existing_user = await self.user_repository.get_by_email(
            request.email,
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError()

        password_hash = hash_password(request.password)

        try:
            user = await self.user_repository.create(
                email=request.email,
                password_hash=password_hash,
                first_name=request.first_name,
                last_name=request.last_name,
            )

            customer_role = await self.role_repository.get_by_name(
                "customer",
            )

            if customer_role is None:
                customer_role = await self.role_repository.create(
                    "customer",
                )

            await self.role_repository.assign_to_user(
                user_id=user.id,
                role_id=customer_role.id,
            )

            await self.session.commit()

            return user

        except Exception:
            await self.session.rollback()
            raise

    async def login(self, request: LoginRequest) -> str:
        """
        Выполняет вход пользователя и возвращает JWT access token.

        Метод:

        1. Ищет пользователя по email.
        2. Проверяет, что пользователь активен.
        3. Проверяет введённый пароль.
        4. Получает роли пользователя.
        5. Создаёт JWT access token.

        Args:
            request: Email и пароль пользователя.

        Returns:
            Подписанный JWT access token.

        Raises:
            InvalidCredentialsError:
                Если пользователь не найден или пароль неверный.
            UserInactiveError:
                Если пользователь заблокирован.
        """
        user = await self.user_repository.get_by_email(
            request.email,
        )

        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        password_is_valid = verify_password(
            request.password,
            user.password_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsError()

        roles = await self.role_repository.get_user_role_names(
            user.id,
        )

        access_token = create_access_token(
            user_id=user.id,
            roles=roles,
        )

        return access_token