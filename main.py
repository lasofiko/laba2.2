from src.models.task import Task
from src.models.task_dataclass import TaskDataClass


def main():
    print("\n1. Создание задачи:")
    task = Task(1, "Написать код", "high")
    print(f"   {task}")


    print("\n2. Изменение состояния:")
    task.start()
    print(f"   После start(): {task.status}")
    task.complete()
    print(f"   После complete(): {task.status}")


    print("\n3. Вычисляемые свойства:")
    print(f"   Завершена: {task.is_completed}")
    print(f"   Уровень приоритета: {task.priority_level}")


    print("\n4. Валидация (пример ошибки):")
    try:
        bad_task = Task("", "Пустой ID")
    except Exception as e:
        print(f"   Ошибка: {e}")


    print("\n5. Dataclass версия:")
    dtask = TaskDataClass(2, "Dataclass задача", "critical")
    print(f"   {dtask}")
    dtask.complete()
    print(f"   После завершения: {dtask.status}")

if __name__ == "__main__":
    main()