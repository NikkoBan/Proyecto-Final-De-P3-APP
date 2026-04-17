
from typing import Optional

from application.dtos.task_dtos import PaginatedTaskResponse, TaskResponse
from domain.entities.task import TaskStatus
from domain.repositories.task_repository import AbstractTaskRepository


class ListTasksUseCase:
    """Return a paginated list of tasks belonging to the authenticated user."""

    def __init__(self, task_repo: AbstractTaskRepository) -> None:
        self._task_repo = task_repo

    async def execute(
        self,
        user_id: int,
        status: Optional[TaskStatus],
        limit: int,
        offset: int,
    ) -> PaginatedTaskResponse:
        tasks, total = await self._task_repo.list_by_user(user_id, status, limit, offset)
        items = [
            TaskResponse(
                id=t.id,  
                title=t.title,
                description=t.description,
                status=t.status,
                priority=t.priority,
                user_id=t.user_id,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tasks
        ]
        return PaginatedTaskResponse(items=items, total=total, limit=limit, offset=offset)
