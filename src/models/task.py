from datetime import datetime
from typing import Optional, Any
from src.descriptors.validators import (
    IdDescriptor,
    DescriptionDescriptor,
    PriorityDescriptor,
    StatusDescriptor,
    NonDataDescriptor
)
from src.exceptions.task_exceptions import TaskStateError, TaskDescriptionError


class Task:

    id = IdDescriptor()
    description = DescriptionDescriptor(mini=1, maxi=500)
    priority = PriorityDescriptor()
    status = StatusDescriptor()

    def __init__(
            self, task_id,
            description, priority = "medium",
            status = "pending", created_at = None
    ):

        self.id = task_id
        self.description = description
        self.priority = priority
        self.status = status

        self._created_at = created_at or datetime.now()
        self._completed_at: Optional[datetime] = None

        self._validate_invariants()

    def _validate_invariants(self):

        if self.status == "completed" and self._completed_at is None:
            raise TaskStateError(
                "Инвариант нарушен: завершенная задача должна иметь дату завершения"
            )

        if self.status == "cancelled":
            if "[Отменено:" not in self.description:
                raise TaskStateError(
                    "Инвариант нарушен: отмененная задача должна иметь причину отмены"
                )

    @property
    def created_at(self):

        return self._created_at

    @property
    def completed_at(self):

        return self._completed_at

    @property
    def is_completed(self):

        return self.status == "completed"

    @property
    def is_active(self):
        return self.status in ["pending", "in_progress"]

    @property
    def priority_level(self):

        return PriorityDescriptor().get_level(self.priority)

    @property
    def age(self):

        delta = datetime.now() - self._created_at
        return delta.total_seconds() / 3600

    @property
    def is_stale(self):

        return self.age > 24 and not self.is_completed

    @NonDataDescriptor
    def is_overdue(self):

        if self.is_completed:
            return False

        if self.priority_level >= 3:  # high или critical
            return self.age > 12 # просрочка через 12 часов
        else:
            return self.age > 24

    def start(self):

        if self.status == "completed":
            raise TaskStateError(
                f"Нельзя начать выполнение завершенной задачи (ID: {self.id})"
            )

        if self.status == "cancelled":
            raise TaskStateError(
                f"Нельзя начать выполнение отмененной задачи (ID: {self.id})"
            )

        self.status = "in_progress"
        return self

    def complete(self):

        if self.status == "completed":
            raise TaskStateError(f"Задача уже завершена (ID: {self.id})")

        if self.status == "cancelled":
            raise TaskStateError(f"Нельзя завершить отмененную задачу (ID: {self.id})")

        self.status = "completed"
        self._completed_at = datetime.now()
        return self

    def cancel(self, reason = None):

        if self.status == "completed":
            raise TaskStateError(
                f"Нельзя отменить завершенную задачу (ID: {self.id})"
            )

        if not reason:
            raise TaskDescriptionError(
                f"Для отмены задачи необходимо указать причину (ID: {self.id})"
            )

        self.status = "cancelled"

        if "[Отменено:" not in self.description:
            self.description = f"{self.description} [Отменено: {reason}]"

        return self

    def __repr__(self):

        return (
            f"Task(id={self.id}, description='{self.description[:30]}...', "
            f"priority={self.priority}, status={self.status})"
        )

    def __str__(self):

        status_display = StatusDescriptor().get_display_name(self.status)
        created_str = self._created_at.strftime("%d.%m.%Y %H:%M")

        lines = [
            f"Задача #{self.id}",
            f"{self.description}",
            f"Приоритет: {self.priority} (уровень {self.priority_level})",
            f"Статус: {status_display}",
            f"Создана: {created_str}",
        ]

        if self._completed_at:
            completed_str = self._completed_at.strftime("%d.%m.%Y %H:%M")
            lines.append(f"Завершена: {completed_str}")

        if self.age > 0:
            lines.append(f"Возраст: {self.age:.1f} ч.")

        if self.is_stale:
            lines.append(f" УСТАРЕЛА ")

        return "\n".join(lines)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
