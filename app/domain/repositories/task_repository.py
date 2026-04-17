
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from domain.entities.task import Task, TaskStatus


class AbstractTaskRepository(ABC):
    """Abstract interface for task persistence. Implementations live in infrastructure."""

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Persist a new task and return it with its generated id."""
        ...

    @abstractmethod
    async def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Retrieve a non-deleted task belonging to the given user."""
        ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        status: Optional[TaskStatus],
        limit: int,
        offset: int,
    ) -> Tuple[List[Task], int]:
        """Return a page of tasks and the total count (for pagination)."""
        ...

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Persist changes to an existing task."""
        ...

    @abstractmethod
    async def soft_delete(self, task_id: int, user_id: int) -> bool:
        """Mark a task as deleted. Returns True if a row was affected."""
        ...
