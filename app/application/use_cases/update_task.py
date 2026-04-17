
from fastapi import HTTPException, status

from application.dtos.task_dtos import TaskResponse, TaskUpdateRequest
from domain.repositories.task_repository import AbstractTaskRepository


class UpdateTaskUseCase:
    """Apply partial updates to an existing task."""

    def __init__(self, task_repo: AbstractTaskRepository) -> None:
        self._task_repo = task_repo

    async def execute(self, task_id: int, user_id: int, request: TaskUpdateRequest) -> TaskResponse:
        task = await self._task_repo.get_by_id(task_id, user_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

        if request.title is not None:
            task.title = request.title
        if request.description is not None:
            task.description = request.description
        if request.status is not None:
            task.status = request.status
        if request.priority is not None:
            task.priority = request.priority

        updated = await self._task_repo.update(task)
        return TaskResponse(
            id=updated.id,  
            title=updated.title,
            description=updated.description,
            status=updated.status,
            priority=updated.priority,
            user_id=updated.user_id,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
