class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных"""
    pass


class InvalidAgeError(DatabaseError):
    """Исключение для недопустимого возраста"""
    pass


class DuplicateIDError(DatabaseError):
    """Исключение для дублирующегося ID"""
    pass


class InvalidSortFieldError(DatabaseError):
    """Исключение для недопустимого поля сортировки"""
    pass
