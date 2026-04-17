
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from infrastructure.database.settings import get_settings

_settings = get_settings()

_ACCESS_DELTA = timedelta(minutes=_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
_REFRESH_DELTA = timedelta(days=_settings.REFRESH_TOKEN_EXPIRE_DAYS)


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": subject, "exp": expire, "type": token_type}
    return jwt.encode(payload, _settings.SECRET_KEY, algorithm=_settings.ALGORITHM)


def create_access_token(user_id: int) -> str:
    """Return a signed JWT access token for the given user id."""
    return _create_token(str(user_id), _ACCESS_DELTA, "access")


def create_refresh_token(user_id: int) -> str:
    """Return a signed JWT refresh token for the given user id."""
    return _create_token(str(user_id), _REFRESH_DELTA, "refresh")


def decode_token(token: str, expected_type: str = "access") -> Optional[int]:
    """
    Decode and validate *token*.

    Returns the user id extracted from the payload, or None if the token is
    invalid, expired, or has an unexpected type.
    """
    try:
        payload = jwt.decode(token, _settings.SECRET_KEY, algorithms=[_settings.ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except (JWTError, ValueError):
        return None
