
from fastapi import HTTPException, status

from domain.repositories.task_repository import AbstractTaskRepository


class DeleteTaskUseCase:
    """Soft-delete a task owned by the authenticated user."""

    def __init__(self, task_repo: AbstractTaskRepository) -> None:
        self._task_repo = task_repo

    async def execute(self, task_id: int, user_id: int) -> None:
        deleted = await self._task_repo.soft_delete(task_id, user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
