
from passlib.context import CryptContext

from infrastructure.database.settings import get_settings

_settings = get_settings()

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=_settings.BCRYPT_ROUNDS,
)


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the *hashed* value."""
    return _pwd_context.verify(plain, hashed)
