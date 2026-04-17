
from fastapi import HTTPException, status

from application.dtos.auth_dtos import RegisterRequest, UserResponse
from application.validators.auth_validators import validate_password_strength
from domain.entities.user import User
from domain.repositories.user_repository import AbstractUserRepository
from infrastructure.security.password_hasher import hash_password


class RegisterUserUseCase:
    """Handle the user registration flow."""

    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, request: RegisterRequest) -> UserResponse:
        """Register a new user. Raises 409 if the email is already taken."""
        validate_password_strength(request.password)

        existing = await self._user_repo.get_by_email(request.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = User(
            email=request.email,
            hashed_password=hash_password(request.password),
        )
        created = await self._user_repo.create(user)
        return UserResponse(id=created.id, email=created.email, is_active=created.is_active)
