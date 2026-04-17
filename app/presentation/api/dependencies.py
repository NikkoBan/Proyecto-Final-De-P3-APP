
"""
Dependency injection wiring.

Each FastAPI dependency function creates the concrete repository/use-case instance
and injects the async DB session from the request scope.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.create_task import CreateTaskUseCase
from application.use_cases.delete_task import DeleteTaskUseCase
from application.use_cases.get_task import GetTaskUseCase
from application.use_cases.list_tasks import ListTasksUseCase
from application.use_cases.login_user import LoginUserUseCase
from application.use_cases.refresh_token import RefreshTokenUseCase
from application.use_cases.register_user import RegisterUserUseCase
from application.use_cases.update_task import UpdateTaskUseCase
from domain.entities.user import User
from infrastructure.database.config import get_db
from infrastructure.repositories.task_repository import SqlTaskRepository
from infrastructure.repositories.user_repository import SqlUserRepository
from infrastructure.security.jwt_handler import decode_token

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()

def get_user_repo(db: AsyncSession = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(db)


def get_task_repo(db: AsyncSession = Depends(get_db)) -> SqlTaskRepository:
    return SqlTaskRepository(db)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    user_repo: SqlUserRepository = Depends(get_user_repo),
) -> User:
    """Validate Bearer token and return the authenticated User."""
    user_id = decode_token(credentials.credentials, expected_type="access")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )
    return user

def get_register_use_case(repo: SqlUserRepository = Depends(get_user_repo)) -> RegisterUserUseCase:
    return RegisterUserUseCase(repo)


def get_login_use_case(repo: SqlUserRepository = Depends(get_user_repo)) -> LoginUserUseCase:
    return LoginUserUseCase(repo)


def get_refresh_use_case(repo: SqlUserRepository = Depends(get_user_repo)) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(repo)


def get_create_task_use_case(repo: SqlTaskRepository = Depends(get_task_repo)) -> CreateTaskUseCase:
    return CreateTaskUseCase(repo)


def get_list_tasks_use_case(repo: SqlTaskRepository = Depends(get_task_repo)) -> ListTasksUseCase:
    return ListTasksUseCase(repo)


def get_get_task_use_case(repo: SqlTaskRepository = Depends(get_task_repo)) -> GetTaskUseCase:
    return GetTaskUseCase(repo)


def get_update_task_use_case(repo: SqlTaskRepository = Depends(get_task_repo)) -> UpdateTaskUseCase:
    return UpdateTaskUseCase(repo)


def get_delete_task_use_case(repo: SqlTaskRepository = Depends(get_task_repo)) -> DeleteTaskUseCase:
    return DeleteTaskUseCase(repo)
