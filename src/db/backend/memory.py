"""In-memory реализация базы данных студентов."""

from typing import Optional, List, Tuple
from .database import DatabaseInterface
from .errors import DuplicateIDError, InvalidAgeError, InvalidSortFieldError

StudentRecord = Tuple[int, str, str, int, str]


class MemoryDatabase(DatabaseInterface):
    """In-memory реализация базы данных студентов."""

    def __init__(self) -> None:
        """Инициализация пустой базы данных."""
        self._students: list[StudentRecord] = []

    def _validate_name(self, name: str, field_name: str) -> str:
        """Проверяет, что имя/фамилия не пустые и не состоят только из пробелов."""
        stripped = name.strip()
        if not stripped:
            raise ValueError(f"Поле '{field_name}' не может быть пустым")
        return stripped

    def _validate_sex(self, sex: str) -> str:
        """Проверяет, что пол указан корректно (M/F)."""
        stripped = sex.strip().upper()
        if stripped not in ('M', 'F'):
            raise ValueError("Поле 'sex' должно быть 'M' или 'F'")
        return stripped

    def create_record(
            self,
            student_id: int,
            first_name: str,
            second_name: str,
            age: int,
            sex: str,
    ) -> StudentRecord:
        """Создаёт новую запись и добавляет её в таблицу."""
        # Проверка возраста
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")

        # Проверка уникальности ID
        if any(record[0] == student_id for record in self._students):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        # Валидация имени, фамилии и пола
        valid_first_name = self._validate_name(first_name, "first_name")
        valid_second_name = self._validate_name(second_name, "second_name")
        valid_sex = self._validate_sex(sex)

        new_record: StudentRecord = (
            student_id,
            valid_first_name,
            valid_second_name,
            age,
            valid_sex,
        )

        self._students.append(new_record)
        return new_record

    def select_record(
            self,
            student_id: Optional[int] = None,
            first_name: Optional[str] = None,
            second_name: Optional[str] = None,
            age: Optional[int] = None,
            sex: Optional[str] = None,
    ) -> List[StudentRecord]:
        """Выполняет выборку записей в соответствии с переданными фильтрами."""
        if (
                student_id is None
                and (first_name is None or first_name == "")
                and (second_name is None or second_name == "")
                and age is None
                and (sex is None or sex == "")
        ):
            return self._students.copy()

        result: List[StudentRecord] = []
        for record in self._students:
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and first_name != "" and record[1] != first_name:
                continue
            if second_name is not None and second_name != "" and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and sex != "" and record[4] != sex.upper():
                continue
            result.append(record)
        return result

    def update_record(
            self,
            student_id: int,
            first_name: Optional[str] = None,
            second_name: Optional[str] = None,
            age: Optional[int] = None,
            sex: Optional[str] = None
    ) -> Optional[StudentRecord]:
        """Обновляет запись с указанным student_id."""
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                # Валидация новых значений
                valid_first_name = record[1]
                valid_second_name = record[2]
                valid_sex = record[4]

                if first_name is not None:
                    valid_first_name = self._validate_name(first_name, "first_name")
                if second_name is not None:
                    valid_second_name = self._validate_name(second_name, "second_name")
                if sex is not None:
                    valid_sex = self._validate_sex(sex)

                new_record = (
                    student_id,
                    valid_first_name,
                    valid_second_name,
                    age if age is not None else record[3],
                    valid_sex,
                )

                if new_record[3] < 0:
                    raise InvalidAgeError("Поле age не может быть отрицательным.")

                self._students[i] = new_record
                return new_record

        return None

    def delete_record(self, student_id: int) -> bool:
        """Удаляет запись с указанным student_id."""
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                del self._students[i]
                return True
        return False

    def get_all_records(self) -> List[StudentRecord]:
        """Возвращает все записи."""
        return self._students.copy()

    def clear(self) -> None:
        """Очищает базу данных."""
        self._students.clear()

    def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
        """Сортирует записи по выбранному полю."""
        field_map = {
            'id': 0,
            'first_name': 1,
            'second_name': 2,
            'age': 3,
            'sex': 4
        }
        if key not in field_map:
            raise InvalidSortFieldError(f"Недопустимое поле: {key}")
        field_index = field_map[key]
        return sorted(self._students, key=lambda record: record[field_index], reverse=reverse)