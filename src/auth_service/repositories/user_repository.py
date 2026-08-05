from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.models import User


class UserRepository:
    """Репозиторий для работы с таблицей пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий пользователей.

        Args:
            session: Асинхронная SQLAlchemy-сессия для работы с PostgreSQL.
        """
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Находит пользователя по его идентификатору.

        Args:
            user_id: Числовой идентификатор пользователя.

        Returns:
            Объект User, если пользователь найден.
            None, если пользователя с таким ID нет.
        """
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """
        Находит пользователя по адресу электронной почты.

        Args:
            email: Email пользователя.

        Returns:
            Объект User, если пользователь найден.
            None, если пользователя с таким email нет.
        """
        statement = select(User).where(User.email == email)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """
        Создаёт нового пользователя и добавляет его в текущую транзакцию.

        Метод не выполняет commit. Фиксацию транзакции должен выполнять
        сервис после завершения всех связанных действий, например после
        создания пользователя и назначения ему роли.

        Args:
            email: Email нового пользователя.
            password_hash: Хеш пароля пользователя.
            first_name: Имя пользователя.
            last_name: Фамилия пользователя.

        Returns:
            Созданный объект User.
        """
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
        )

        self.session.add(user)

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def update_profile(
        self,
        user: User,
        *,
        first_name: str | None,
        last_name: str | None,
    ) -> User:
        """
        Обновляет имя и фамилию пользователя.

        Метод не выполняет commit.

        Args:
            user: Пользователь, данные которого нужно изменить.
            first_name: Новое имя пользователя.
            last_name: Новая фамилия пользователя.

        Returns:
            Обновлённый объект User.
        """
        user.first_name = first_name
        user.last_name = last_name

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def update_password_hash(
        self,
        user: User,
        password_hash: str,
    ) -> User:
        """
        Обновляет хеш пароля пользователя.

        Репозиторий получает уже готовый хеш. Хеширование обычного пароля
        должно выполняться в security- или service-слое.

        Метод не выполняет commit.

        Args:
            user: Пользователь, которому нужно изменить пароль.
            password_hash: Новый хеш пароля.

        Returns:
            Обновлённый объект User.
        """
        user.password_hash = password_hash

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def set_active(
        self,
        user: User,
        is_active: bool,
    ) -> User:
        """
        Изменяет состояние активности пользователя.

        False означает, что пользователь заблокирован.
        True означает, что пользователь активен.

        Метод не выполняет commit.

        Args:
            user: Пользователь, состояние которого нужно изменить.
            is_active: Новое состояние активности.

        Returns:
            Обновлённый объект User.
        """
        user.is_active = is_active

        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def list_users(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]:
        """
        Возвращает список пользователей с пагинацией.

        Args:
            limit: Максимальное количество пользователей в ответе.
            offset: Количество пользователей, которые нужно пропустить.

        Returns:
            Список объектов User.
        """
        statement = (
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def delete(self, user: User) -> None:
        """
        Удаляет пользователя из базы данных.

        Метод не выполняет commit.

        Args:
            user: Пользователь, которого нужно удалить.
        """
        await self.session.delete(user)
        await self.session.flush()