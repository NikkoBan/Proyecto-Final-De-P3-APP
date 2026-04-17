
from fastapi import HTTPException, status

from application.dtos.auth_dtos import RefreshRequest, TokenResponse
from domain.repositories.user_repository import AbstractUserRepository
from infrastructure.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class RefreshTokenUseCase:
    """Issue a new token pair from a valid refresh token."""

    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, request: RefreshRequest) -> TokenResponse:
        """Decode the refresh token and return a fresh pair."""
        user_id = decode_token(request.refresh_token, expected_type="refresh")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )

        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
