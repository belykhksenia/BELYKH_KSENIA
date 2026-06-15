"""Тесты для in-memory базы данных."""

import pytest
from src.db.backend import MemoryDatabase, InvalidAgeError, DuplicateIDError, InvalidSortFieldError


class TestMemoryDatabase:

    @pytest.fixture
    def db(self):
        db = MemoryDatabase()
        db.clear()
        return db

    def test_create_record_success(self, db):
        record = db.create_record(1, "Иван", "Петров", 20, "M")
        assert record[0] == 1
        assert record[1] == "Иван"
        assert record[2] == "Петров"
        assert record[3] == 20
        assert record[4] == "M"

    def test_create_record_empty_first_name(self, db):
        with pytest.raises(ValueError, match="Поле 'first_name' не может быть пустым"):
            db.create_record(1, "  ", "Петров", 20, "M")

    def test_create_record_empty_second_name(self, db):
        with pytest.raises(ValueError, match="Поле 'second_name' не может быть пустым"):
            db.create_record(1, "Иван", "  ", 20, "M")

    def test_create_record_invalid_sex(self, db):
        with pytest.raises(ValueError, match="Поле 'sex' должно быть 'M' или 'F'"):
            db.create_record(1, "Иван", "Петров", 20, "X")

    def test_create_record_negative_age(self, db):
        with pytest.raises(InvalidAgeError, match="Поле age не может быть отрицательным"):
            db.create_record(1, "Иван", "Петров", -5, "M")

    def test_create_record_duplicate_id(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        with pytest.raises(DuplicateIDError, match="Запись с id=1 уже существует"):
            db.create_record(1, "Петр", "Сидоров", 25, "M")

    def test_select_all_empty(self, db):
        records = db.select_record()
        assert records == []

    def test_select_all_with_data(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        records = db.select_record()
        assert len(records) == 2

    def test_select_by_id(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        records = db.select_record(student_id=1)
        assert len(records) == 1
        assert records[0][1] == "Иван"

    def test_select_by_first_name(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Иван", "Сидоров", 25, "M")
        records = db.select_record(first_name="Иван")
        assert len(records) == 2

    def test_update_record_success(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        updated = db.update_record(1, age=25)
        assert updated[3] == 25

    def test_update_record_not_found(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        result = db.update_record(999, age=25)
        assert result is None

    def test_delete_record_success(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        result = db.delete_record(1)
        assert result is True
        assert len(db.get_all_records()) == 0

    def test_delete_record_not_found(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        result = db.delete_record(999)
        assert result is False

    def test_sort_by_age(self, db):
        db.create_record(1, "Иван", "Петров", 30, "M")
        db.create_record(2, "Мария", "Иванова", 20, "F")
        db.create_record(3, "Петр", "Сидоров", 25, "M")

        sorted_records = db.sort_records("age")
        assert sorted_records[0][3] == 20
        assert sorted_records[1][3] == 25
        assert sorted_records[2][3] == 30

    def test_sort_by_id_desc(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        sorted_records = db.sort_records("id", reverse=True)
        assert sorted_records[0][0] == 2
        assert sorted_records[1][0] == 1

    def test_clear(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.clear()
        assert len(db.get_all_records()) == 0

    def test_sort_invalid_field(self, db):
        with pytest.raises(InvalidSortFieldError):
            db.sort_records("invalid")

    def test_database_interface_complete(self, db):
        """Полное тестирование интерфейса database.py."""
        record = db.create_record(100, "Интерфейс", "Тест", 25, "M")
        assert record[0] == 100

        records = db.select_record(student_id=100, first_name="Интерфейс",
                                   second_name="Тест", age=25, sex="M")
        assert len(records) == 1

        records = db.select_record(first_name="", second_name="", sex="")
        assert len(records) >= 1

        updated = db.update_record(100, age=26)
        assert updated[3] == 26

        updated = db.update_record(100, first_name="Обновлено")
        assert updated[1] == "Обновлено"

        result = db.update_record(999, age=30)
        assert result is None

        all_records = db.get_all_records()
        assert len(all_records) >= 1

        deleted = db.delete_record(100)
        assert deleted is True

        deleted = db.delete_record(999)
        assert deleted is False

        db.clear()
        assert len(db.get_all_records()) == 0

    def test_sort_by_sex(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        db.create_record(3, "Анна", "Сидорова", 25, "F")

        sorted_records = db.sort_records("sex")
        assert sorted_records[0][4] == "F"

    def test_sort_by_first_name_desc(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Анна", "Иванова", 22, "F")
        db.create_record(3, "Борис", "Сидоров", 25, "M")

        sorted_records = db.sort_records("first_name", reverse=True)
        assert sorted_records[0][1] == "Иван"

    def test_get_all_records_empty_db(self, db):
        db.clear()
        records = db.get_all_records()
        assert records == []

    def test_select_with_none_values(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")

        records = db.select_record(student_id=None, first_name=None,
                                   second_name=None, age=None, sex=None)
        assert len(records) == 1