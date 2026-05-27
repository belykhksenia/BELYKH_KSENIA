"""Backend модуль с реализациями базы данных."""

from .table import StudentTable
from .memory import MemoryDatabase
from .file import JSONDatabase, CSVDatabase
from .errors import (
    DatabaseError,
    InvalidAgeError,
    DuplicateIDError,
    InvalidSortFieldError,
    DatabaseNotFoundError,
    DatabaseLoadError,
    DatabaseSaveError,
)

__all__ = [
    'StudentTable',
    'MemoryDatabase',
    'JSONDatabase',
    'CSVDatabase',
    'DatabaseError',
    'InvalidAgeError',
    'DuplicateIDError',
    'InvalidSortFieldError',
    'DatabaseNotFoundError',
    'DatabaseLoadError',
    'DatabaseSaveError',
]
