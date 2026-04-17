from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dtos.auth_dtos import LoginRequest, RegisterRequest
from application.use_cases.login_user import LoginUserUseCase
from application.use_cases.register_user import RegisterUserUseCase
from domain.entities.user import User
from infrastructure.security.password_hasher import hash_password


@pytest.mark.asyncio
class TestRegisterUserUseCase:
    async def test_register_creates_user_successfully(self):
        repo = AsyncMock()
        repo.get_by_email.return_value = None
        new_user = User(id=1, email="test@example.com", hashed_password="hashed")
        repo.create.return_value = new_user

        use_case = RegisterUserUseCase(repo)
        result = await use_case.execute(RegisterRequest(email="test@example.com", password="securepass"))

        assert result.email == "test@example.com"
        assert result.id == 1
        repo.create.assert_called_once()

    async def test_register_raises_409_on_duplicate_email(self):
        from fastapi import HTTPException

        repo = AsyncMock()
        repo.get_by_email.return_value = User(id=1, email="test@example.com", hashed_password="x")

        use_case = RegisterUserUseCase(repo)
        with pytest.raises(HTTPException) as exc:
            await use_case.execute(RegisterRequest(email="test@example.com", password="securepass"))

        assert exc.value.status_code == 409

    async def test_register_raises_422_on_short_password(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RegisterRequest(email="x@x.com", password="short")


@pytest.mark.asyncio
class TestLoginUserUseCase:
    async def test_login_returns_tokens_on_valid_credentials(self):
        password = "correctpassword"
        repo = AsyncMock()
        repo.get_by_email.return_value = User(
            id=1,
            email="user@test.com",
            hashed_password=hash_password(password),
            is_active=True,
        )

        use_case = LoginUserUseCase(repo)
        result = await use_case.execute(LoginRequest(email="user@test.com", password=password))

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"

    async def test_login_raises_401_on_wrong_password(self):
        from fastapi import HTTPException

        repo = AsyncMock()
        repo.get_by_email.return_value = User(
            id=1, email="u@u.com", hashed_password=hash_password("realpassword"), is_active=True
        )

        use_case = LoginUserUseCase(repo)
        with pytest.raises(HTTPException) as exc:
            await use_case.execute(LoginRequest(email="u@u.com", password="wrongpassword"))

        assert exc.value.status_code == 401

    async def test_login_raises_401_when_user_not_found(self):
        from fastapi import HTTPException

        repo = AsyncMock()
        repo.get_by_email.return_value = None

        use_case = LoginUserUseCase(repo)
        with pytest.raises(HTTPException) as exc:
            await use_case.execute(LoginRequest(email="ghost@x.com", password="any"))

        assert exc.value.status_code == 401
