
from fastapi import HTTPException, status

from application.dtos.task_dtos import TaskResponse
from domain.repositories.task_repository import AbstractTaskRepository


class GetTaskUseCase:
    """Retrieve a single task by id, scoped to the authenticated user."""

    def __init__(self, task_repo: AbstractTaskRepository) -> None:
        self._task_repo = task_repo

    async def execute(self, task_id: int, user_id: int) -> TaskResponse:
        task = await self._task_repo.get_by_id(task_id, user_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return TaskResponse(
            id=task.id,  
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
