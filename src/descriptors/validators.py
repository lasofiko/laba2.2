from typing import Optional, Callable
from datetime import datetime
from src.exceptions.task_exceptions import (
    TaskIdError,
    TaskDescriptionError,
    TaskPriorityError,
    TaskStatusError
)

class ValidatorDescriptor:

    def __init__(self, name = None):
        self.name = name
        self._private_name = None

    def __set_name__(self, owner, name):

        self.name = name
        self._private_name = f"_{name}"

    def __get__(self, i, owner):

        if i is None:
            return self
        return getattr(i, self._private_name, None)

    def __set__(self, instance, value):

        validated_value = self.validate(value)
        setattr(instance, self._private_name, validated_value)

    def validate(self, value):

        raise NotImplementedError("Дочерний класс должен реализовать validate()")


class NonDataDescriptor:

    def __init__(self, func):
        self.func = func
        self.name = None

    def __set_name__(self, owner, name):

        self.name = name

    def __get__(self, i, owner):

        if i is None:
            return self
        return self.func(i)


class IdDescriptor(ValidatorDescriptor):

    def validate(self, value):

        if value is None:
            raise TaskIdError("ID задачи не может быть None")

        if value == "":
            raise TaskIdError("ID задачи не может быть пустой строкой")

        if not isinstance(value, (int, str)):
            raise TaskIdError(
                f"ID должен быть числом или строкой, "
                f"получен {type(value).__name__}"
            )

        return str(value)


class DescriptionDescriptor(ValidatorDescriptor):

    def __init__(self, mini: int = 1, maxi: int = 500, name = None):
        super().__init__(name)
        #вызов конструктора родительского класса,
        # super() возвращает временный объект родительского класса
        # позволяет обращаться к методам родительского класса
        self.mini = mini
        self.maxi = maxi

    def validate(self, value):

        if value is None:
            raise TaskDescriptionError("Описание задачи не может быть None")

        if not isinstance(value, str):
            raise TaskDescriptionError(
                f"Описание должно быть строкой, "
                f"получен {type(value).__name__}"
            )

        value = value.strip()

        if len(value) < self.mini:
            raise TaskDescriptionError(
                f"Описание слишком короткое: "
                f"минимум {self.mini} символ(ов), "
                f"получено {len(value)}"
            )

        if len(value) > self.maxi:
            raise TaskDescriptionError(
                f"Описание слишком длинное: "
                f"максимум {self.maxi} символ(ов), "
                f"получено {len(value)}"
            )

        return value


class PriorityDescriptor(ValidatorDescriptor):

    priority = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }

    def validate(self, value):

        if value is None:
            return "medium"

        if isinstance(value, int):
            for name, level in self.priority.items():
                if level == value:
                    return name

            raise TaskPriorityError(
                f"Некорректный числовой приоритет: {value}. "
                f"Допустимые значения: 1-low, 2-medium, "
                f"3-high, 4-critical"
            )

        if isinstance(value, str):
            value_lower = value.lower()

            if value_lower in self.priority:
                return value_lower

            raise TaskPriorityError(
                f"Некорректный приоритет: {value}. "
                f"Допустимые значения: low, medium, high, critical"
            )

        raise TaskPriorityError(
            f"Приоритет должен быть строкой или числом, "
            f"получен {type(value).__name__}"
        )

    def get_level(self, priority: str) -> int:

        return self.priority.get(priority, 0)


class StatusDescriptor(ValidatorDescriptor):

    statuses = {
        "pending": "Ожидает выполнения",
        "in_progress": "В процессе",
        "completed": "Завершена",
        "cancelled": "Отменена"
    }

    def validate(self, value):

        if value is None:
            return "pending"

        if not isinstance(value, str):
            raise TaskStatusError(
                f"Статус должен быть строкой, "
                f"получен {type(value).__name__}"
            )

        value_lower = value.lower()

        if value_lower in self.statuses:
            return value_lower

        raise TaskStatusError(
            f"Некорректный статус: {value}. "
            f"Допустимые значения: {', '.join(self.statuses.keys())}"
        )

    def get_display_name(self, status: str) -> str:

        return self.statuses.get(status, status)