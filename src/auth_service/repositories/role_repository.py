from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.database.models import Role, UserRole


class RoleRepository:
    """Репозиторий для работы с ролями пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий ролей.

        Args:
            session: Асинхронная SQLAlchemy-сессия.
        """
        self.session = session

    async def get_by_name(self, name: str) -> Role | None:
        """
        Находит роль по имени.

        Args:
            name: Имя роли, например customer или admin.

        Returns:
            Найденная роль либо None.
        """
        statement = select(Role).where(Role.name == name)
        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self, name: str) -> Role:
        """
        Создаёт роль в текущей транзакции.

        Метод не выполняет commit.

        Args:
            name: Имя создаваемой роли.

        Returns:
            Созданная роль.
        """
        role = Role(name=name)

        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)

        return role

    async def assign_to_user(
        self,
        *,
        user_id: int,
        role_id: int,
    ) -> UserRole:
        """
        Назначает роль пользователю.

        Метод создаёт запись в таблице user_roles и не выполняет commit.

        Args:
            user_id: ID пользователя.
            role_id: ID назначаемой роли.

        Returns:
            Созданная связь пользователя с ролью.
        """
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        self.session.add(user_role)
        await self.session.flush()

        return user_role

    async def get_user_role_names(self, user_id: int) -> list[str]:
        """
        Возвращает названия всех ролей пользователя.

        Args:
            user_id: ID пользователя.

        Returns:
            Список имён ролей, например ["customer"].
        """
        statement = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())