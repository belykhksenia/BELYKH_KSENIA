"""Класс таблицы студентов."""

from typing import Optional, List, Tuple
from .errors import DuplicateIDError, InvalidAgeError, InvalidSortFieldError

type StudentRecord = tuple[int, str, str, int, str]


class StudentTable:
    def __init__(self) -> None:
        self._students: list[StudentRecord] = []

    def create_record(
            self,
            student_id: int,
            first_name: str,
            second_name: str,
            age: int,
            sex: str,
    ) -> StudentRecord:
        """
        Создаёт новую запись и добавляет её в таблицу Student.
        """
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")

        if any(record[0] == student_id for record in self._students):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
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
            if sex is not None and sex != "" and record[4] != sex:
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
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                new_record = (
                    student_id,
                    first_name if first_name is not None else record[1],
                    second_name if second_name is not None else record[2],
                    age if age is not None else record[3],
                    sex if sex is not None else record[4]
                )

                if new_record[3] < 0:
                    raise InvalidAgeError("Поле age не может быть отрицательным.")

                self._students[i] = new_record
                return new_record

        return None

    def delete_record(self, student_id: int) -> bool:
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                del self._students[i]
                return True

        return False

    def get_all_records(self) -> List[StudentRecord]:
        return self._students.copy()

    def clear(self) -> None:
        self._students.clear()

    def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
        field_map = {
            'id': 0,
            'first_name': 1,
            'second_name': 2,
            'age': 3,
            'sex': 4
        }

        if key not in field_map:
            raise InvalidSortFieldError(
                f"Недопустимое поле для сортировки: {key}. "
                f"Допустимые поля: {list(field_map.keys())}"
            )

        field_index = field_map[key]
        return sorted(self._students, key=lambda record: record[field_index], reverse=reverse)