
from fastapi import HTTPException, status


def validate_password_strength(password: str) -> None:
    """Raise HTTP 422 if the password does not meet minimum requirements."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )
