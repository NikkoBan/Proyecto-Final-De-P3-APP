
from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.user import User


class AbstractUserRepository(ABC):
    """Abstract interface for user persistence. Implementations live in infrastructure."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their primary key."""
        ...

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user and return it with its generated id."""
        ...
