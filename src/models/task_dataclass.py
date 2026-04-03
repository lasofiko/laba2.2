from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from src.descriptors.validators import (
    IdDescriptor,
    DescriptionDescriptor,
    PriorityDescriptor,
    StatusDescriptor
)
from src.exceptions.task_exceptions import TaskStateError, TaskDescriptionError

@dataclass
class TaskDataClass:

    _id = IdDescriptor()
    _description = DescriptionDescriptor(mini=1, maxi=500)
    _priority = PriorityDescriptor()
    _status = StatusDescriptor()

    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = field(default=None)

    def __init__(
            self, task_id,
            description, priority = "medium",
            status = "pending", created_at = None
    ):
        
        self._id = task_id
        self._description = description
        self._priority = priority
        self._status = status
        self.created_at = created_at or datetime.now()
        self.completed_at = None
        self._validate_invariants()

    @property
    def id(self) -> str:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def priority(self) -> str:
        return self._priority

    @priority.setter
    def priority(self, value: Any):
        self._priority = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    def _validate_invariants(self):
        if self.status == "completed" and self.completed_at is None:
            raise TaskStateError("Завершенная задача должна иметь дату завершения")

        if self.status == "cancelled" and "[Отменено:" not in self.description:
            raise TaskStateError("Отмененная задача должна иметь причину отмены")

    @property
    def priority_level(self):
        return PriorityDescriptor().get_level(self.priority)

    @property
    def is_completed(self):
        return self.status == "completed"

    def start(self):
        if self.status == "completed":
            raise TaskStateError("Нельзя начать завершенную задачу")
        if self.status == "cancelled":
            raise TaskStateError("Нельзя начать отмененную задачу")

        self.status = "in_progress"
        return self

    def complete(self):
        if self.status == "completed":
            raise TaskStateError("Задача уже завершена")
        if self.status == "cancelled":
            raise TaskStateError("Нельзя завершить отмененную задачу")

        self.status = "completed"
        self.completed_at = datetime.now()
        return self

    def cancel(self, reason=None):
        if self.status == "completed":
            raise TaskStateError("Нельзя отменить завершенную задачу")

        if not reason:
            raise TaskDescriptionError("Для отмены необходимо указать причину")

        self.status = "cancelled"
        if "[Отменено:" not in self.description:
            self.description = f"{self.description} [Отменено: {reason}]"
        return self

    def __repr__(self):
        return f"TaskDataClass(id={self.id}, status={self.status})"
