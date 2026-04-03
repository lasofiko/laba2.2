# Лабораторная работа №2

## Модель задачи: дескрипторы и @property

### Цель работы

Освоить управление доступом к атрибутам и защиту инвариантов доменной модели через:
- Пользовательские дескрипторы (data и non-data)
- Property для вычисляемых свойств
- Специализированные исключения

### Реализованные компоненты

#### 1. Дескрипторы валидации 
- **Data descriptors**: `IdDescriptor`, `DescriptionDescriptor`, `PriorityDescriptor`, `StatusDescriptor`
- **Non-data descriptor**: `NonDataDescriptor` для вычисляемых свойств

#### 2. Специализированные исключения 
- `TaskError` - базовое исключение
- `TaskIdError` - ошибки ID
- `TaskDescriptionError` - ошибки описания
- `TaskPriorityError` - ошибки приоритета
- `TaskStatusError` - ошибки статуса
- `TaskStateError` - ошибки состояния

#### 3. Модель Task 
- Валидация всех атрибутов через дескрипторы
- Property только для чтения (`created_at`, `completed_at`)
- Вычисляемые property (`is_completed`, `is_active`, `age`, `is_stale`)
- Non-data descriptor (`is_overdue`)
- Конечный автомат состояний (`start()`, `complete()`, `cancel()`)
- Защита инвариантов
- Магические методы (`__repr__`, `__str__`, `__eq__`, `__hash__`)
