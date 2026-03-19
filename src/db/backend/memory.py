from typing import Optional, List
from .errors import DuplicateIDError, InvalidAgeError

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
        # Проверка корректности возраста
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")

        # Проверка уникальности идентификатора
        if any(record[0] == student_id for record in self._students):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        # Формирование новой записи
        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )

        # Добавление записи в таблицу
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
        """
        Выполняет выборку записей из таблицы Student
        в соответствии с переданными фильтрами.
        """
        # Проверка отсутствия всех фильтров
        if (
                student_id is None
                and first_name is None
                and second_name is None
                and age is None
                and sex is None
        ):
            return self._students.copy()

        # Формирование результирующего списка
        result: List[StudentRecord] = []

        # Итерация по всем записям таблицы
        for record in self._students:
            # Проверка соответствия каждому фильтру
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1] != first_name:
                continue
            if second_name is not None and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and record[4] != sex:
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
        """
        Обновляет запись с указанным student_id.
        Возвращает обновленную запись или None, если запись не найдена.
        """
        # Ищем запись по id
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                # Создаем новую запись с обновленными полями
                new_record = (
                    student_id,
                    first_name if first_name is not None else record[1],
                    second_name if second_name is not None else record[2],
                    age if age is not None else record[3],
                    sex if sex is not None else record[4]
                )

                # Валидация возраста
                if new_record[3] < 0:
                    raise InvalidAgeError("Поле age не может быть отрицательным.")

                # Заменяем запись
                self._students[i] = new_record
                return new_record

        # Если запись не найдена
        return None

    def delete_record(self, student_id: int) -> bool:
        """
        Удаляет запись с указанным student_id.
        Возвращает True, если запись была удалена, иначе False.
        """
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                del self._students[i]
                return True

        return False

    def get_all_records(self) -> List[StudentRecord]:
        """Возвращает все записи в таблице"""
        return self._students.copy()

    def clear(self) -> None:
        """Очищает таблицу (для тестирования)"""
        self._students.clear()


def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
    """
    Сортирует записи по выбранному полю.

    Args:
        key: Поле для сортировки ('id', 'first_name', 'second_name', 'age', 'sex')
        reverse: False - по возрастанию, True - по убыванию

    Returns:
        Отсортированный список записей
    """
    field_map = {
        'id': 0,
        'first_name': 1,
        'second_name': 2,
        'age': 3,
        'sex': 4
    }

    if key not in field_map:
        raise ValueError(f"Недопустимое поле для сортировки: {key}. Допустимые поля: {list(field_map.keys())}")

    field_index = field_map[key]
    return sorted(self._students, key=lambda record: record[field_index], reverse=reverse)