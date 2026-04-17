
from fastapi import APIRouter, Depends

from application.dtos.auth_dtos import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from application.use_cases.login_user import LoginUserUseCase
from application.use_cases.refresh_token import RefreshTokenUseCase
from application.use_cases.register_user import RegisterUserUseCase
from presentation.api.dependencies import (
    get_login_use_case,
    get_refresh_use_case,
    get_register_use_case,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
) -> UserResponse:
    """Register a new user account."""
    return await use_case.execute(body)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    """Authenticate and receive JWT tokens."""
    return await use_case.execute(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_use_case),
) -> TokenResponse:
    """Exchange a refresh token for a fresh token pair."""
    return await use_case.execute(body)
