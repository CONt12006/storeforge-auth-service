from fastapi import APIRouter, Depends, HTTPException, status

from auth_service.api.dependencies import get_auth_service
from auth_service.schemas.auth import LoginRequest, RegisterRequest
from auth_service.schemas.token import TokenResponse
from auth_service.schemas.user import UserResponse
from auth_service.services.auth_service import (
    AuthService,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserInactiveError,
)

from auth_service.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
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
    """
    Регистрирует нового пользователя.

    Args:
        request: Данные регистрации.
        service: Сервис регистрации и авторизации.

    Returns:
        Данные созданного пользователя.

    Raises:
        HTTPException: Если пользователь с таким email уже существует.
    """
    try:
        user = await service.register(request)

    except EmailAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        ) from error

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        access_token, refresh_token = await service.login(
            request
        )

    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        ) from error

    except UserInactiveError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь заблокирован",
        ) from error

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    request: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        access_token, refresh_token = await service.refresh(
            request.refresh_token
        )

    except InvalidRefreshTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token недействителен или уже использован",
        ) from error

    except UserInactiveError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь заблокирован",
        ) from error

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )