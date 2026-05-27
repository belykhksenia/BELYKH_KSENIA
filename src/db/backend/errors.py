"""Исключения для работы с базой данных."""


class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных."""
    pass


class InvalidAgeError(DatabaseError):
    """Исключение для недопустимого возраста."""
    pass


class DuplicateIDError(DatabaseError):
    """Исключение для дублирующегося ID."""
    pass


class InvalidSortFieldError(DatabaseError):
    """Исключение для недопустимого поля сортировки."""
    pass


class DatabaseNotFoundError(DatabaseError):
    """Исключение, когда файл базы данных не найден."""
    pass


class DatabaseLoadError(DatabaseError):
    """Исключение при ошибке загрузки базы данных."""
    pass


class DatabaseSaveError(DatabaseError):
    """Исключение при ошибке сохранения базы данных."""
    pass