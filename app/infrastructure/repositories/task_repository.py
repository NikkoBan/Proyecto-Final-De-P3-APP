
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.task import Task, TaskPriority, TaskStatus
from domain.repositories.task_repository import AbstractTaskRepository
from infrastructure.database.models import TaskModel


class SqlTaskRepository(AbstractTaskRepository):
    """SQLAlchemy implementation of AbstractTaskRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            priority=TaskPriority(model.priority),
            is_deleted=model.is_deleted,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, task: Task) -> Task:
        model = TaskModel(
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        result = await self._session.execute(
            select(TaskModel).where(
                TaskModel.id == task_id,
                TaskModel.user_id == user_id,
                TaskModel.is_deleted.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user(
        self,
        user_id: int,
        status: Optional[TaskStatus],
        limit: int,
        offset: int,
    ) -> Tuple[List[Task], int]:
        base_where = [TaskModel.user_id == user_id, TaskModel.is_deleted.is_(False)]
        if status is not None:
            base_where.append(TaskModel.status == status.value)

        total_result = await self._session.execute(
            select(func.count()).select_from(TaskModel).where(*base_where)
        )
        total = total_result.scalar_one()

        rows_result = await self._session.execute(
            select(TaskModel)
            .where(*base_where)
            .order_by(TaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        tasks = [self._to_entity(m) for m in rows_result.scalars().all()]
        return tasks, total

    async def update(self, task: Task) -> Task:
        await self._session.execute(
            update(TaskModel)
            .where(TaskModel.id == task.id, TaskModel.user_id == task.user_id)
            .values(
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                updated_at=datetime.utcnow(),
            )
        )
        await self._session.flush()
        return await self.get_by_id(task.id, task.user_id)  

    async def soft_delete(self, task_id: int, user_id: int) -> bool:
        result = await self._session.execute(
            update(TaskModel)
            .where(
                TaskModel.id == task_id,
                TaskModel.user_id == user_id,
                TaskModel.is_deleted.is_(False),
            )
            .values(is_deleted=True, updated_at=datetime.utcnow())
        )
        await self._session.flush()
        return result.rowcount > 0
