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


class LogoutRequest(BaseModel):
    """Запрос завершения пользовательской сессии."""

    refresh_token: str = Field(
        min_length=32
    )


class RefreshRequest(BaseModel):
    """Запрос на обновление пары access/refresh токенов"""

    refresh_token: str


class TokenResponse(BaseModel):
    """
    Ответ с новой парой токенов после успешной
    аутентификации или обновления сессии.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
