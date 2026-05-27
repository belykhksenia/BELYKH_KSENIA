"""Файловые реализации базы данных (JSON, CSV) с поддержкой индексации."""

import os
import json
import csv
from typing import Optional, List, Tuple, Dict
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

    def _create_index(self, field_name: str, field_index: int) -> None:
        if field_name not in self._indices:
            self._indices[field_name] = {}
        index = self._indices[field_name]
        for record in self._students:
            value = record[field_index]
            if value not in index:
                index[value] = set()
            index[value].add(record[0])

    def _add_to_index(self, record: StudentRecord) -> None:
        field_indices = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        for field_name, idx in field_indices.items():
            if field_name in self._indices:
                value = record[idx]
                if value not in self._indices[field_name]:
                    self._indices[field_name][value] = set()
                self._indices[field_name][value].add(record[0])

    def _remove_from_index(self, record: StudentRecord) -> None:
        field_indices = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        for field_name, idx in field_indices.items():
            if field_name in self._indices:
                value = record[idx]
                if value in self._indices[field_name]:
                    self._indices[field_name][value].discard(record[0])
                    if not self._indices[field_name][value]:
                        del self._indices[field_name][value]

    def _load(self) -> None:
        if not os.path.exists(self.filepath):
            self._students = []
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
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
        try:
            data = {
                'students': [list(record) for record in self._students],
                'indices': {}
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
        field_map = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        if field_name not in field_map:
            raise InvalidSortFieldError(f"Недопустимое поле: {field_name}")
        self._create_index(field_name, field_map[field_name])
        self._save()

    def get_indices(self) -> Dict[str, int]:
        return {f: len(idx) for f, idx in self._indices.items()}

    def create_record(self, student_id: int, first_name: str, second_name: str, age: int, sex: str) -> StudentRecord:
        if age < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным")
        if any(r[0] == student_id for r in self._students):
            raise DuplicateIDError(f"ID {student_id} уже существует")
        record = (student_id, first_name.strip(), second_name.strip(), age, sex.strip())
        self._students.append(record)
        self._add_to_index(record)
        self._save()
        return record

    def select_record(self, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> List[StudentRecord]:
        if all(v is None or v == "" for v in [student_id, first_name, second_name, age, sex]):
            return self._students.copy()

        # Поиск по индексу если есть
        if student_id is not None and 'id' in self._indices:
            if student_id in self._indices['id']:
                for r in self._students:
                    if r[0] == student_id:
                        return [r]
            return []

        result = []
        for r in self._students:
            if student_id is not None and r[0] != student_id: continue
            if first_name and first_name != "" and r[1] != first_name: continue
            if second_name and second_name != "" and r[2] != second_name: continue
            if age is not None and r[3] != age: continue
            if sex and sex != "" and r[4] != sex: continue
            result.append(r)
        return result

    def update_record(self, student_id: int, first_name=None, second_name=None, age=None, sex=None) -> Optional[StudentRecord]:
        for i, r in enumerate(self._students):
            if r[0] == student_id:
                new_record = (
                    student_id,
                    first_name if first_name else r[1],
                    second_name if second_name else r[2],
                    age if age is not None else r[3],
                    sex if sex else r[4]
                )
                if new_record[3] < 0:
                    raise InvalidAgeError("Возраст не может быть отрицательным")
                self._remove_from_index(r)
                self._students[i] = new_record
                self._add_to_index(new_record)
                self._save()
                return new_record
        return None

    def delete_record(self, student_id: int) -> bool:
        for i, r in enumerate(self._students):
            if r[0] == student_id:
                self._remove_from_index(r)
                del self._students[i]
                self._save()
                return True
        return False

    def get_all_records(self) -> List[StudentRecord]:
        return self._students.copy()

    def clear(self) -> None:
        self._students.clear()
        self._indices.clear()
        self._save()

    def sort_records(self, key: str, reverse: bool = False) -> List[StudentRecord]:
        field_map = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        if key not in field_map:
            raise InvalidSortFieldError(f"Недопустимое поле: {key}")
        return sorted(self._students, key=lambda r: r[field_map[key]], reverse=reverse)


class CSVDatabase(DatabaseInterface):
    """CSV файловая БД."""

    def __init__(self, filepath: str = "data/database.csv"):
        self.filepath = filepath
        self._students: list[StudentRecord] = []
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        self._load()

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
        record = (student_id, first_name.strip(), second_name.strip(), age, sex.strip())
        self._students.append(record)
        self._save()
        return record

    def select_record(self, student_id=None, first_name=None, second_name=None, age=None, sex=None) -> List[StudentRecord]:
        if all(v is None or v == "" for v in [student_id, first_name, second_name, age, sex]):
            return self._students.copy()
        result = []
        for r in self._students:
            if student_id is not None and r[0] != student_id: continue
            if first_name and first_name != "" and r[1] != first_name: continue
            if second_name and second_name != "" and r[2] != second_name: continue
            if age is not None and r[3] != age: continue
            if sex and sex != "" and r[4] != sex: continue
            result.append(r)
        return result

    def update_record(self, student_id: int, first_name=None, second_name=None, age=None, sex=None) -> Optional[StudentRecord]:
        for i, r in enumerate(self._students):
            if r[0] == student_id:
                new_record = (
                    student_id,
                    first_name if first_name else r[1],
                    second_name if second_name else r[2],
                    age if age is not None else r[3],
                    sex if sex else r[4]
                )
                if new_record[3] < 0:
                    raise InvalidAgeError("Возраст не может быть отрицательным")
                self._students[i] = new_record
                self._save()
                return new_record
        return None

    def delete_record(self, student_id: int) -> bool:
        for i, r in enumerate(self._students):
            if r[0] == student_id:
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