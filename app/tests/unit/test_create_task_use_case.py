from unittest.mock import AsyncMock
from datetime import datetime

import pytest

from application.dtos.task_dtos import TaskCreateRequest
from application.use_cases.create_task import CreateTaskUseCase
from application.use_cases.delete_task import DeleteTaskUseCase
from domain.entities.task import Task, TaskPriority, TaskStatus


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=1, title="Test Task", user_id=1,
        status=TaskStatus.PENDING, priority=TaskPriority.MEDIUM,
        is_deleted=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    defaults.update(kwargs)
    return Task(**defaults)


@pytest.mark.asyncio
class TestCreateTaskUseCase:
    async def test_create_returns_task_response(self):
        repo = AsyncMock()
        repo.create.return_value = _make_task(title="My Task")

        use_case = CreateTaskUseCase(repo)
        result = await use_case.execute(
            TaskCreateRequest(title="My Task", status=TaskStatus.PENDING, priority=TaskPriority.LOW),
            user_id=1,
        )
        assert result.title == "My Task"
        assert result.id == 1
        repo.create.assert_called_once()

    async def test_create_passes_user_id(self):
        repo = AsyncMock()
        repo.create.return_value = _make_task(user_id=42)

        use_case = CreateTaskUseCase(repo)
        await use_case.execute(
            TaskCreateRequest(title="Task", status=TaskStatus.PENDING, priority=TaskPriority.HIGH),
            user_id=42,
        )
        created_task: Task = repo.create.call_args[0][0]
        assert created_task.user_id == 42


@pytest.mark.asyncio
class TestDeleteTaskUseCase:
    async def test_delete_raises_404_when_not_found(self):
        from fastapi import HTTPException

        repo = AsyncMock()
        repo.soft_delete.return_value = False

        use_case = DeleteTaskUseCase(repo)
        with pytest.raises(HTTPException) as exc:
            await use_case.execute(task_id=99, user_id=1)

        assert exc.value.status_code == 404

    async def test_delete_succeeds(self):
        repo = AsyncMock()
        repo.soft_delete.return_value = True

        use_case = DeleteTaskUseCase(repo)
        await use_case.execute(task_id=1, user_id=1)
        repo.soft_delete.assert_called_once_with(1, 1)
