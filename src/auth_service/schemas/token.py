from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Ответ после успешного входа."""

    access_token: str
    token_type: str = "bearer"