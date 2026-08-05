from fastapi import APIRouter, Depends, HTTPException, status

from auth_service.api.dependencies import get_auth_service
from auth_service.schemas.auth import RegisterRequest
from auth_service.schemas.user import UserResponse
from auth_service.services.auth_service import (
    AuthService,
    EmailAlreadyExistsError,
)


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Регистрирует нового пользователя."""

    try:
        user = await service.register(request)
    except EmailAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        ) from error

    return UserResponse.model_validate(user)