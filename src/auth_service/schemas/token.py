from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Пара access/refresh токенов."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
