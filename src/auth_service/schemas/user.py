from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    """Данные пользователя, возвращаемые клиенту."""

    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)