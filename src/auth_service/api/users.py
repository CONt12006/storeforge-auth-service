from fastapi import APIRouter, Depends

from auth_service.api.dependencies import get_current_user
from auth_service.database.models import User
from auth_service.schemas.user import UserResponse


router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Возвращает данные текущего пользователя.

    Пользователь определяется по JWT из Authorization header.
    """
    return UserResponse.model_validate(current_user)