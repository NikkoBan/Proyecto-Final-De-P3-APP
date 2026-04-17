
from typing import Optional

from fastapi import APIRouter, Depends, Query

from application.dtos.task_dtos import (
    PaginatedTaskResponse,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
)
from application.use_cases.create_task import CreateTaskUseCase
from application.use_cases.delete_task import DeleteTaskUseCase
from application.use_cases.get_task import GetTaskUseCase
from application.use_cases.list_tasks import ListTasksUseCase
from application.use_cases.update_task import UpdateTaskUseCase
from domain.entities.task import TaskStatus
from domain.entities.user import User
from presentation.api.dependencies import (
    get_create_task_use_case,
    get_current_user,
    get_delete_task_use_case,
    get_get_task_use_case,
    get_list_tasks_use_case,
    get_update_task_use_case,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    """Create a new task for the authenticated user."""
    return await use_case.execute(body, current_user.id)  


@router.get("", response_model=PaginatedTaskResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    use_case: ListTasksUseCase = Depends(get_list_tasks_use_case),
) -> PaginatedTaskResponse:
    """List tasks for the authenticated user with optional status filter and pagination."""
    return await use_case.execute(current_user.id, status, limit, offset)  


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    use_case: GetTaskUseCase = Depends(get_get_task_use_case),
) -> TaskResponse:
    """Get a single task by id."""
    return await use_case.execute(task_id, current_user.id)  


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    body: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateTaskUseCase = Depends(get_update_task_use_case),
) -> TaskResponse:
    """Update a task's fields."""
    return await use_case.execute(task_id, current_user.id, body)  


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case),
) -> None:
    """Soft-delete a task."""
    await use_case.execute(task_id, current_user.id)  
