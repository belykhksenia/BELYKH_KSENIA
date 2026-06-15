"""Файловые реализации базы данных (JSON, CSV) с поддержкой индексации."""

import os
import json
import csv
from typing import Optional, List, Tuple, Dict, Set
from .database import DatabaseInterface
from .errors import (
    DuplicateIDError, InvalidAgeError, InvalidSortFieldError,
    DatabaseLoadError, DatabaseSaveError
)

StudentRecord = Tuple[int, str, str, int, str]


class JSONDatabase(DatabaseInterface):
    """JSON файловая БД с поддержкой индексов."""

    def __init__(self, filepath: str = "data/database.json"):
        self.filepath = filepath
        self._students: list[StudentRecord] = []
        self._indices: Dict[str, Dict] = {}
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        self._load()

    def _validate_name(self, name: str, field_name: str) -> str:
        """Проверяет, что имя/фамилия не пустые."""
        stripped = name.strip()
        if not stripped:
            raise ValueError(f"Поле '{field_name}' не может быть пустым")
        return stripped

    def _validate_sex(self, sex: str) -> str:
        """Проверяет, что пол указан корректно."""
        stripped = sex.strip().upper()
        if stripped not in ('M', 'F'):
            raise ValueError("Поле 'sex' должно быть 'M' или 'F'")
        return stripped

    def _create_index(self, field_name: str, field_index: int) -> None:
        """Создаёт индекс для указанного поля."""
        if field_name not in self._indices:
            self._indices[field_name] = {}
        index = self._indices[field_name]
        for record in self._students:
            value = record[field_index]
            if value not in index:
                index[value] = set()
            index[value].add(record[0])

    def _add_to_index(self, record: StudentRecord) -> None:
        """Добавляет запись во все индексы."""
        field_indices = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        for field_name, idx in field_indices.items():
            if field_name in self._indices:
                value = record[idx]
                if value not in self._indices[field_name]:
                    self._indices[field_name][value] = set()
                self._indices[field_name][value].add(record[0])

    def _remove_from_index(self, record: StudentRecord) -> None:
        """Удаляет запись из всех индексов."""
        field_indices = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        for field_name, idx in field_indices.items():
            if field_name in self._indices:
                value = record[idx]
                if value in self._indices[field_name]:
                    self._indices[field_name][value].discard(record[0])
                    if not self._indices[field_name][value]:
                        del self._indices[field_name][value]

    def _load(self) -> None:
        """Загружает данные из JSON файла."""
        if not os.path.exists(self.filepath):
            self._students = []
            self._indices = {}
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Загружаем структуру таблицы и записи
            self._students = [tuple(record) for record in data.get('students', [])]
            indices_data = data.get('indices', {})
            self._indices = {}
            for field_name, index_data in indices_data.items():
                self._indices[field_name] = {}
                for value, ids in index_data.items():
                    converted_value = int(value) if field_name in ['id', 'age'] else value
                    self._indices[field_name][converted_value] = set(ids)
        except Exception as e:
            raise DatabaseLoadError(f"Ошибка загрузки JSON: {e}")

    def _save(self) -> None:
        """Сохраняет данные в JSON файл (структура таблицы + записи + индексы)."""
        try:
            data = {
                'students': [list(record) for record in self._students],
                'indices': {},
                'schema': {
                    'columns': ['id', 'first_name', 'second_name', 'age', 'sex'],
                    'types': ['int', 'str', 'str', 'int', 'str']
                }
            }
            for field_name, index in self._indices.items():
                data['indices'][field_name] = {}
                for value, ids in index.items():
                    data['indices'][field_name][str(value)] = list(ids)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise DatabaseSaveError(f"Ошибка сохранения JSON: {e}")

    def create_index(self, field_name: str) -> None:
        """Создаёт индекс для указанного поля."""
        field_map = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        if field_name not in field_map:
            raise InvalidSortFieldError(f"Недопустимое поле: {field_name}")
        self._create_index(field_name, field_map[field_name])
        self._save()

    def get_indices(self) -> Dict[str, int]:
        """Возвращает информацию о существующих индексах."""
        return {f: len(idx) for f, idx in self._indices.items()}

    def create_record(self, student_id: int, first_name: str, second_name: str, age: int, sex: str) -> StudentRecord:
        """Создаёт новую запись."""
        if age < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        if any(r[0] == student_id for r in self._students):
            raise DuplicateIDError(f"ID {student_id} уже существует")

        # Валидация
        valid_first_name = self._validate_name(first_name, "first_name")
        valid_second_name = self._validate_name(second_name, "second_name")
        valid_sex = self._validate_sex(sex)

        record = (student_id, valid_first_name, valid_second_name, age, valid_sex)
        self._students.append(record)
        self._add_to_index(record)
        self._save()
        return record

    def select_record(self, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> List[
        StudentRecord]:
        """Выполняет выборку записей с использованием индексов."""
        # Если нет фильтров - возвращаем всё
        if all(v is None or v == "" for v in [student_id, first_name, second_name, age, sex]):
            return self._students.copy()

        # Определяем, по какому полю можно использовать индекс
        index_used = None
        index_value = None

        if student_id is not None and 'id' in self._indices:
            index_used = 'id'
            index_value = student_id
        elif first_name is not None and first_name != "" and 'first_name' in self._indices:
            index_used = 'first_name'
            index_value = first_name
        elif second_name is not None and second_name != "" and 'second_name' in self._indices:
            index_used = 'second_name'
            index_value = second_name
        elif age is not None and 'age' in self._indices:
            index_used = 'age'
            index_value = age
        elif sex is not None and sex != "" and 'sex' in self._indices:
            index_used = 'sex'
            index_value = sex.upper()

        # Если есть индекс - получаем кандидатов по индексу
        if index_used is not None:
            if index_value in self._indices[index_used]:
                candidate_ids = self._indices[index_used][index_value]
            else:
                return []

            # Фильтруем записи по индексу и дополнительным условиям
            result = []
            for record in self._students:
                if record[0] not in candidate_ids:
                    continue
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

        # Без индекса - линейный поиск
        result = []
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

    def update_record(self, student_id: int, first_name=None, second_name=None, age=None, sex=None) -> Optional[
        StudentRecord]:
        """Обновляет запись."""
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                # Валидация новых значений
                new_first_name = record[1]
                new_second_name = record[2]
                new_sex = record[4]

                if first_name is not None:
                    new_first_name = self._validate_name(first_name, "first_name")
                if second_name is not None:
                    new_second_name = self._validate_name(second_name, "second_name")
                if sex is not None:
                    new_sex = self._validate_sex(sex)

                new_record = (
                    student_id,
                    new_first_name,
                    new_second_name,
                    age if age is not None else record[3],
                    new_sex
                )
                if new_record[3] < 0:
                    raise InvalidAgeError("Возраст не может быть отрицательным")

                self._remove_from_index(record)
                self._students[i] = new_record
                self._add_to_index(new_record)
                self._save()
                return new_record
        return None

    def delete_record(self, student_id: int) -> bool:
        """Удаляет запись."""
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                self._remove_from_index(record)
                del self._students[i]
                self._save()
                return True
        return False

    def get_all_records(self) -> List[StudentRecord]:
        """Возвращает все записи."""
        return self._students.copy()

    def clear(self) -> None:
        """Очищает БД."""
        self._students.clear()
        self._indices.clear()
        self._save()

    def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
        """Сортирует записи."""
        field_map = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        if key not in field_map:
            raise InvalidSortFieldError(f"Недопустимое поле: {key}")
        return sorted(self._students, key=lambda r: r[field_map[key]], reverse=reverse)


class CSVDatabase(DatabaseInterface):
    """CSV файловая БД (без индексов)."""

    def __init__(self, filepath: str = "data/database.csv"):
        self.filepath = filepath
        self._students: list[StudentRecord] = []
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        self._load()

    def _validate_name(self, name: str, field_name: str) -> str:
        stripped = name.strip()
        if not stripped:
            raise ValueError(f"Поле '{field_name}' не может быть пустым")
        return stripped

    def _validate_sex(self, sex: str) -> str:
        stripped = sex.strip().upper()
        if stripped not in ('M', 'F'):
            raise ValueError("Поле 'sex' должно быть 'M' или 'F'")
        return stripped

    def _load(self) -> None:
        if not os.path.exists(self.filepath):
            self._students = []
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                next(reader, None)
                self._students = []
                for row in reader:
                    if len(row) == 5:
                        self._students.append((int(row[0]), row[1], row[2], int(row[3]), row[4]))
        except Exception as e:
            raise DatabaseLoadError(f"Ошибка загрузки CSV: {e}")

    def _save(self) -> None:
        try:
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'first_name', 'second_name', 'age', 'sex'])
                writer.writerows(self._students)
        except Exception as e:
            raise DatabaseSaveError(f"Ошибка сохранения CSV: {e}")

    def create_record(self, student_id: int, first_name: str, second_name: str, age: int, sex: str) -> StudentRecord:
        if age < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        if any(r[0] == student_id for r in self._students):
            raise DuplicateIDError(f"ID {student_id} уже существует")

        valid_first_name = self._validate_name(first_name, "first_name")
        valid_second_name = self._validate_name(second_name, "second_name")
        valid_sex = self._validate_sex(sex)

        record = (student_id, valid_first_name, valid_second_name, age, valid_sex)
        self._students.append(record)
        self._save()
        return record

    def select_record(self, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> List[
        StudentRecord]:
        if all(v is None or v == "" for v in [student_id, first_name, second_name, age, sex]):
            return self._students.copy()
        result = []
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

    def update_record(self, student_id: int, first_name=None, second_name=None, age=None, sex=None) -> Optional[
        StudentRecord]:
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                new_first_name = record[1]
                new_second_name = record[2]
                new_sex = record[4]

                if first_name is not None:
                    new_first_name = self._validate_name(first_name, "first_name")
                if second_name is not None:
                    new_second_name = self._validate_name(second_name, "second_name")
                if sex is not None:
                    new_sex = self._validate_sex(sex)

                new_record = (
                    student_id,
                    new_first_name,
                    new_second_name,
                    age if age is not None else record[3],
                    new_sex
                )
                if new_record[3] < 0:
                    raise InvalidAgeError("Возраст не может быть отрицательным")
                self._students[i] = new_record
                self._save()
                return new_record
        return None

    def delete_record(self, student_id: int) -> bool:
        for i, record in enumerate(self._students):
            if record[0] == student_id:
                del self._students[i]
                self._save()
                return True
        return False

    def get_all_records(self) -> List[StudentRecord]:
        return self._students.copy()

    def clear(self) -> None:
        self._students.clear()
        self._save()

    def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
        field_map = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        if key not in field_map:
            raise InvalidSortFieldError(f"Недопустимое поле: {key}")
        return sorted(self._students, key=lambda r: r[field_map[key]], reverse=reverse)