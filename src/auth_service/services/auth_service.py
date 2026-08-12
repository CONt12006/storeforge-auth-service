from sqlalchemy.ext.asyncio import AsyncSession

import hmac
from datetime import datetime, timezone

from auth_service.database.models import User
from auth_service.repositories.role_repository import RoleRepository
from auth_service.repositories.user_repository import UserRepository
from auth_service.schemas.auth import LoginRequest, RegisterRequest
from auth_service.security.jwt import create_access_token
from auth_service.security.password import hash_password, verify_password


from auth_service.config import settings
from auth_service.repositories.refresh_token_repository import RefreshTokenRepository
from auth_service.security.refresh_token import InvalidRefreshTokenFormatError, generate_refresh_token, get_session_id, hash_refresh_token


class InvalidRefreshTokenError(Exception):
    """Refresh token недействителен."""


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
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.refresh_token_repository = refresh_token_repository

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

    async def login(
        self,
        request: LoginRequest,
    ) -> tuple[str, str]:
        user = await self.user_repository.get_by_email(
            request.email
        )
    
        if user is None:
            raise InvalidCredentialsError()
    
        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError()
    
        if not user.is_active:
            raise UserInactiveError()
    
        return await self._issue_token_pair(user)

    async def _issue_token_pair(
        self,
        user: User,
    ) -> tuple[str, str]:
        roles = (
            await self.role_repository.get_user_role_names(
                user.id
            )
        )
    
        access_token = create_access_token(
            user_id=user.id,
            roles=roles,
        )
    
        session_id, refresh_token = (
            generate_refresh_token()
        )
    
        await self.refresh_token_repository.save(
            session_id=session_id,
            user_id=user.id,
            token_hash=hash_refresh_token(
                refresh_token
            ),
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
            ttl_seconds=(
                settings.refresh_token_expire_days
                * 24
                * 60
                * 60
            ),
        )
    
        return access_token, refresh_token

    
    async def refresh(
        self,
        refresh_token: str,
    ) -> tuple[str, str]:
        try:
            session_id = get_session_id(
                refresh_token
            )
        except InvalidRefreshTokenFormatError as error:
            raise InvalidRefreshTokenError() from error
    
        session = (
            await self.refresh_token_repository.get(
                session_id
            )
        )
    
        if session is None:
            raise InvalidRefreshTokenError()
    
        expected_hash = session["token_hash"]
    
        actual_hash = hash_refresh_token(
            refresh_token
        )
    
        if not hmac.compare_digest(
            expected_hash,
            actual_hash,
        ):
            raise InvalidRefreshTokenError()
    
        user = await self.user_repository.get_by_id(
            int(session["user_id"])
        )
    
        if user is None:
            await self.refresh_token_repository.delete(
                session_id
            )
    
            raise InvalidRefreshTokenError()
    
        if not user.is_active:
            await (
                self.refresh_token_repository
                .delete_all_for_user(user.id)
            )
    
            raise UserInactiveError()
    
    
        await self.refresh_token_repository.delete(
            session_id
        )
    
        return await self._issue_token_pair(user)


    async def logout(
        self,
        refresh_token: str,
    ) -> None:
        try:
            session_id = get_session_id(
                refresh_token
            )
        except InvalidRefreshTokenFormatError:
            return
    
        session = (
            await self.refresh_token_repository.get(
                session_id
            )
        )
    
        if session is None:
            return
    
        expected_hash = session["token_hash"]
    
        actual_hash = hash_refresh_token(
            refresh_token
        )
    
        if hmac.compare_digest(
            expected_hash,
            actual_hash,
        ):
            await self.refresh_token_repository.delete(
                session_id
            )
    
    
    async def logout_all(
        self,
        user_id: int,
    ) -> None:
        await (
            self.refresh_token_repository
            .delete_all_for_user(user_id)
        )
