
from fastapi import HTTPException, status

from application.dtos.auth_dtos import LoginRequest, TokenResponse
from domain.repositories.user_repository import AbstractUserRepository
from infrastructure.security.jwt_handler import create_access_token, create_refresh_token
from infrastructure.security.password_hasher import verify_password


class LoginUserUseCase:
    """Authenticate a user and return JWT tokens."""

    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, request: LoginRequest) -> TokenResponse:
        """Validate credentials and return access + refresh tokens."""
        user = await self._user_repo.get_by_email(request.email)
        if user is None or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled.",
            )

        return TokenResponse(
            access_token=create_access_token(user.id),  
            refresh_token=create_refresh_token(user.id),  
        )
