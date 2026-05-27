"""Абстрактный интерфейс для всех реализаций базы данных."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

StudentRecord = Tuple[int, str, str, int, str]


class DatabaseInterface(ABC):
    """Интерфейс для всех реализаций БД."""

    @abstractmethod
    def create_record(self, student_id: int, first_name: str, second_name: str, age: int, sex: str) -> StudentRecord:
        """Создаёт новую запись."""
        pass

    @abstractmethod
    def select_record(self, student_id: Optional[int] = None, first_name: Optional[str] = None,
                      second_name: Optional[str] = None, age: Optional[int] = None,
                      sex: Optional[str] = None) -> List[StudentRecord]:
        """Выполняет выборку записей."""
        pass

    @abstractmethod
    def update_record(self, student_id: int, first_name: Optional[str] = None,
                      second_name: Optional[str] = None, age: Optional[int] = None,
                      sex: Optional[str] = None) -> Optional[StudentRecord]:
        """Обновляет запись."""
        pass

    @abstractmethod
    def delete_record(self, student_id: int) -> bool:
        """Удаляет запись."""
        pass

    @abstractmethod
    def get_all_records(self) -> List[StudentRecord]:
        """Возвращает все записи."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очищает базу данных."""
        pass

    @abstractmethod
    def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
        """Сортирует записи."""
        pass