from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Данные для регистрации пользователя."""

    email: EmailStr
    password: str = Field(min_length=4, max_length=128)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    """Данные для входа пользователя."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)