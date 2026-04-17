
from application.dtos.task_dtos import TaskCreateRequest, TaskResponse
from domain.entities.task import Task
from domain.repositories.task_repository import AbstractTaskRepository


class CreateTaskUseCase:
    """Create a new task owned by the authenticated user."""

    def __init__(self, task_repo: AbstractTaskRepository) -> None:
        self._task_repo = task_repo

    async def execute(self, request: TaskCreateRequest, user_id: int) -> TaskResponse:
        task = Task(
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            user_id=user_id,
        )
        created = await self._task_repo.create(task)
        return TaskResponse(
            id=created.id,  
            title=created.title,
            description=created.description,
            status=created.status,
            priority=created.priority,
            user_id=created.user_id,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
