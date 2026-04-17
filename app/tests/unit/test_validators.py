import pytest
from pydantic import ValidationError

from application.dtos.task_dtos import TaskCreateRequest
from application.dtos.auth_dtos import RegisterRequest
from domain.entities.task import TaskPriority, TaskStatus


class TestTaskDtoValidation:
    def test_title_too_short_raises(self):
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="ab", status=TaskStatus.PENDING, priority=TaskPriority.LOW)

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="x" * 101, status=TaskStatus.PENDING, priority=TaskPriority.LOW)

    def test_valid_task_passes(self):
        dto = TaskCreateRequest(title="Valid Title", status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)
        assert dto.title == "Valid Title"

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="Valid", status="flying", priority=TaskPriority.LOW)

    def test_invalid_priority_raises(self):
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="Valid", status=TaskStatus.PENDING, priority="extreme")


class TestAuthDtoValidation:
    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="not-an-email", password="validpass")

    def test_valid_registration_passes(self):
        dto = RegisterRequest(email="user@example.com", password="securepass")
        assert dto.email == "user@example.com"
