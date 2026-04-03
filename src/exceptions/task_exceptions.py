# Наследуется от встроенного класса Exception, все остальные исключения будут наследоваться от TaskError

class TaskError(Exception):
    pass
# некорректная идентификация задач
class TaskIdError(TaskError):
     pass

# некорректное описание
class TaskDescriptionError(TaskError):
    pass

# некорректный приоритет
class TaskPriorityError(TaskError):
     pass

# некорректный статус
class TaskStatusError(TaskError):
    pass

# ошибка перехода между состояниями
class TaskStateError(TaskError):
     pass