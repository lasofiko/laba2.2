import pytest
from datetime import datetime, timedelta
from src.models.task import Task
from src.models.task_dataclass import TaskDataClass
from src.exceptions.task_exceptions import (
    TaskIdError,
    TaskDescriptionError,
    TaskPriorityError,
    TaskStatusError,
    TaskStateError
)

def assert_task_basics(task, expected_id, expected_description):

    assert task.id == str(expected_id)
    assert task.description == expected_description
    assert task.created_at is not None

class TestTaskCreation:

    def test_create_valid_task(self):
        task = Task(1, "Тестовая задача", "high", "pending")

        assert task.id == "1"
        assert task.description == "Тестовая задача"
        assert task.priority == "high"
        assert task.status == "pending"
        assert task.priority_level == 3

    def test_default_values(self):
        task = Task(1, "Тест")
        assert task.priority == "medium"
        assert task.status == "pending"

    def test_numeric_priority(self):
        task = Task(1, "Тест", priority=4)
        assert task.priority == "critical"

    def test_custom_created_at(self):
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        task = Task(1, "Тест", created_at=custom_time)
        assert task.created_at == custom_time


class TestValidation:

    def test_id_validation(self):

        with pytest.raises(TaskIdError):
            Task("", "Тест")
        with pytest.raises(TaskIdError):
            Task(None, "Тест")
        with pytest.raises(TaskIdError):
            Task([1, 2], "Тест")

        assert Task(123, "Тест").id == "123"

    def test_description_validation(self):

        with pytest.raises(TaskDescriptionError):
            Task(1, "")
        with pytest.raises(TaskDescriptionError):
            Task(1, "a" * 501)

        task = Task(1, "  Норм описание  ")
        assert task.description == "Норм описание"

    def test_priority_validation(self):

        with pytest.raises(TaskPriorityError):
            Task(1, "Тест", priority="urgent")
        with pytest.raises(TaskPriorityError):
            Task(1, "Тест", priority=5)

        for p in ["low", "medium", "high", "critical", 1, 2, 3, 4]:
            task = Task(1, "Тест", priority=p)
            assert task.priority in ["low", "medium", "high", "critical"]

    def test_status_validation(self):

        with pytest.raises(TaskStatusError):
            Task(1, "Тест", status="done")

        task = Task(1, "Тест", status=None)
        assert task.status == "pending"


class TestStateTransitions:

    def test_normal_flow(self):

        task = Task(1, "Тест")
        assert task.status == "pending"

        task.start()
        assert task.status == "in_progress"

        task.complete()
        assert task.status == "completed"
        assert task.completed_at is not None

    def test_cancel_flow(self):

        task = Task(1, "Тест")
        task.cancel("Не требуется")
        assert task.status == "cancelled"
        assert "[Отменено:" in task.description

    def test_invalid_transitions(self):

        task = Task(1, "Тест")
        task.complete()

        with pytest.raises(TaskStateError):
            task.start()

        task = Task(1, "Тест")
        task.cancel("Причина")

        with pytest.raises(TaskStateError):
            task.complete()

    def test_cancel_requires_reason(self):

        task = Task(1, "Тест")
        with pytest.raises(TaskDescriptionError):
            task.cancel()

    def test_chained_methods(self):

        task = Task(1, "Тест")
        task.start().complete()
        assert task.status == "completed"


class TestComputedProperties:

    def test_boolean_properties(self):

        task = Task(1, "Тест")
        assert not task.is_completed
        assert task.is_active

        task.complete()
        assert task.is_completed
        assert not task.is_active

    def test_priority_level(self):

        assert Task(1, "Тест", "low").priority_level == 1
        assert Task(1, "Тест", "medium").priority_level == 2
        assert Task(1, "Тест", "high").priority_level == 3
        assert Task(1, "Тест", "critical").priority_level == 4

    def test_age_and_stale(self):

        fresh = Task(1, "Тест")
        assert fresh.age < 1
        assert not fresh.is_stale

        old_time = datetime.now() - timedelta(hours=25)
        old = Task(2, "Тест", created_at=old_time)
        assert old.age > 24
        assert old.is_stale

        old.complete()
        assert not old.is_stale


class TestNonDataDescriptor:

    def test_is_overdue(self):

        fresh = Task(1, "Тест")
        assert fresh.is_overdue is False

        old_low = datetime.now() - timedelta(hours=25)
        low_task = Task(2, "Тест", "low", created_at=old_low)
        assert low_task.is_overdue is True

        old_high = datetime.now() - timedelta(hours=13)
        high_task = Task(3, "Тест", "high", created_at=old_high)
        assert high_task.is_overdue is True

    def test_override(self):

        task = Task(1, "Тест")
        original = task.is_overdue

        task.is_overdue = True
        assert task.is_overdue is True

        del task.is_overdue
        assert task.is_overdue == original


class TestReadonlyProperties:

    def test_created_at_readonly(self):
        task = Task(1, "Тест")
        with pytest.raises(AttributeError):
            task.created_at = datetime.now()

    def test_completed_at_readonly(self):
        task = Task(1, "Тест")
        with pytest.raises(AttributeError):
            task.completed_at = datetime.now()


class TestMagicMethods:

    def test_repr(self):
        task = Task(1, "Тестовая задача")
        assert "Task(id=1" in repr(task)
        assert "Тестовая задача" in repr(task)

    def test_str(self):
        task = Task(1, "Тестовая задача")
        str_str = str(task)
        assert "Задача #1" in str_str
        assert "Тестовая задача" in str_str

    def test_equality_and_hash(self):

        t1 = Task(1, "А")
        t2 = Task(1, "Б")
        t3 = Task(2, "А")

        assert t1 == t2
        assert t1 != t3

        task_set = {t1, t2, t3}
        assert len(task_set) == 2

class TestInvariants:

    def test_completed_needs_date(self):

        task = Task(1, "Тест")
        task.complete()
        assert task.completed_at is not None

        with pytest.raises(TaskStateError):
            Task(1, "Тест", status="completed")

    def test_cancelled_needs_reason(self):

        with pytest.raises(TaskStateError):
            Task(1, "Тест", status="cancelled")

class TestDataClassTask:

    def test_creation(self):

        task = TaskDataClass(1, "Dataclass задача", "high")

        assert task.id == "1"
        assert task.description == "Dataclass задача"
        assert task.priority == "high"
        assert task.status == "pending"
        assert task.priority_level == 3

    def test_default_values(self):

        task = TaskDataClass(1, "Тест")
        assert task.priority == "medium"
        assert task.status == "pending"

    def test_numeric_priority(self):

        task = TaskDataClass(1, "Тест", priority=4)
        assert task.priority == "critical"

    def test_validation(self):

        with pytest.raises(TaskIdError):
            TaskDataClass("", "Тест")

        with pytest.raises(TaskDescriptionError):
            TaskDataClass(1, "")

        with pytest.raises(TaskPriorityError):
            TaskDataClass(1, "Тест", priority="urgent")

    def test_state_transitions(self):

        task = TaskDataClass(1, "Тест")

        task.start()
        assert task.status == "in_progress"

        task.complete()
        assert task.status == "completed"
        assert task.completed_at is not None

    def test_cancel(self):

        task = TaskDataClass(1, "Тест")
        task.cancel("Не нужно")
        assert task.status == "cancelled"

    def test_properties(self):

        task = TaskDataClass(1, "Тест", "high")
        assert task.priority_level == 3
        assert not task.is_completed

        task.complete()
        assert task.is_completed

    def test_repr(self):

        task = TaskDataClass(1, "Тест")
        assert "TaskDataClass" in repr(task)
        assert "id=1" in repr(task)

class TestBothImplementations:

    @pytest.mark.parametrize("TaskClass", [Task, TaskDataClass])
    def test_both_have_same_interface(self, TaskClass):

        task = TaskClass(1, "Общий тест", "high")

        assert hasattr(task, 'id')
        assert hasattr(task, 'description')
        assert hasattr(task, 'priority')
        assert hasattr(task, 'status')

        assert hasattr(task, 'start')
        assert hasattr(task, 'complete')

        assert hasattr(task, 'priority_level')
        assert hasattr(task, 'is_completed')

    @pytest.mark.parametrize("TaskClass", [Task, TaskDataClass])
    def test_both_validate_correctly(self, TaskClass):

        with pytest.raises(TaskIdError):
            TaskClass("", "Тест")

        with pytest.raises(TaskDescriptionError):
            TaskClass(1, "")

    @pytest.mark.parametrize("TaskClass", [Task, TaskDataClass])
    def test_both_handle_state(self, TaskClass):

        task = TaskClass(1, "Тест")
        task.start()
        assert task.status == "in_progress"

        task.complete()
        assert task.status == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])