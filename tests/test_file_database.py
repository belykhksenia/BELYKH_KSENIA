"""Тесты для файловых баз данных."""

import pytest
import os
import json
import csv
from src.db.backend import JSONDatabase, CSVDatabase, InvalidAgeError, DuplicateIDError


class TestJSONDatabase:
    """Тесты для JSON БД (с поддержкой индексов)."""

    @pytest.fixture
    def db_path(self, tmp_path):
        return str(tmp_path / "test_db.json")

    @pytest.fixture
    def db(self, db_path):
        db = JSONDatabase(db_path)
        db.clear()
        return db

    def test_create_and_persist(self, db_path):
        db1 = JSONDatabase(db_path)
        db1.create_record(1, "Иван", "Петров", 20, "M")

        db2 = JSONDatabase(db_path)
        records = db2.get_all_records()
        assert len(records) == 1
        assert records[0][1] == "Иван"

    def test_create_index(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        db.create_index("age")

        indices = db.get_indices()
        assert "age" in indices

    def test_select_with_index(self, db):
        db.create_index("first_name")
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        db.create_record(3, "Иван", "Сидоров", 25, "M")

        records = db.select_record(first_name="Иван")
        assert len(records) == 2

        def test_load_empty_file(self, tmp_path):
            """Тест загрузки пустого файла."""
            db_path = str(tmp_path / "empty.json")
            # Создаём пустой файл
            with open(db_path, 'w') as f:
                f.write('{}')

            db = JSONDatabase(db_path)
            assert len(db.get_all_records()) == 0

        def test_load_corrupted_json(self, tmp_path):
            """Тест загрузки повреждённого JSON."""
            db_path = str(tmp_path / "corrupt.json")
            with open(db_path, 'w') as f:
                f.write('{corrupted json}')

            from src.db.backend.errors import DatabaseLoadError
            with pytest.raises(DatabaseLoadError):
                JSONDatabase(db_path)

        def test_save_permission_error(self, db, monkeypatch):
            """Тест ошибки сохранения."""

            def mock_open(*args, **kwargs):
                raise OSError("Permission denied")

            monkeypatch.setattr("builtins.open", mock_open)

            from src.db.backend.errors import DatabaseSaveError
            with pytest.raises(DatabaseSaveError):
                db.create_record(99, "Тест", "Тестов", 20, "M")

        def test_select_by_age_without_index(self, db):
            """Тест поиска по возрасту без индекса."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record(age=20)
            assert len(records) == 1
            assert records[0][1] == "Иван"

        def test_select_with_nonexistent_value(self, tmp_path):
            """Тест поиска с несуществующим значением."""
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            records = db.select_record(first_name="Несуществующее")
            assert len(records) == 0

        def test_select_with_second_name_filter(self, tmp_path):
            """Тест поиска по фамилии."""
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record(second_name="Петров")
            assert len(records) == 1
            assert records[0][1] == "Иван"

        def test_select_by_sex_without_index(self, db):
            """Тест поиска по полу без индекса."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record(sex="M")
            assert len(records) == 1
            assert records[0][1] == "Иван"

        def test_select_multiple_filters_with_index(self, db):
            """Тест поиска с несколькими фильтрами и индексом."""
            db.create_index("first_name")

            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Иван", "Сидоров", 25, "M")
            db.create_record(3, "Петр", "Петров", 30, "M")

            records = db.select_record(first_name="Иван", age=25)
            assert len(records) == 1
            assert records[0][2] == "Сидоров"

    def test_delete_with_index(self, db):
        db.create_index("first_name")
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        db.delete_record(1)
        records = db.select_record(first_name="Иван")
        assert len(records) == 0

    def test_update_with_index(self, db):
        db.create_index("first_name")
        db.create_record(1, "Иван", "Петров", 20, "M")

        db.update_record(1, first_name="Петр")
        records = db.select_record(first_name="Петр")
        assert len(records) == 1
        assert records[0][1] == "Петр"

    def test_update_record_nonexistent(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        result = db.update_record(999, age=25)
        assert result is None

    def test_update_record_age_negative(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        with pytest.raises(InvalidAgeError):
            db.update_record(1, age=-5)

    def test_create_multiple_indices(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        db.create_index("age")
        db.create_index("sex")

        indices = db.get_indices()
        assert "age" in indices
        assert "sex" in indices

    def test_select_with_index_and_extra_filter(self, db):
        db.create_index("first_name")

        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Иван", "Сидоров", 25, "M")
        db.create_record(3, "Иван", "Иванов", 30, "M")

        records = db.select_record(first_name="Иван", age=25)
        assert len(records) == 1
        assert records[0][2] == "Сидоров"

    def test_select_without_matching_index(self, db):
        db.create_index("first_name")

        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        records = db.select_record(first_name="Петр")
        assert len(records) == 0

    def test_update_record_updates_index(self, db):
        db.create_index("first_name")

        db.create_record(1, "Иван", "Петров", 20, "M")

        records = db.select_record(first_name="Иван")
        assert len(records) == 1

        db.update_record(1, first_name="Петр")

        records = db.select_record(first_name="Иван")
        assert len(records) == 0

        records = db.select_record(first_name="Петр")
        assert len(records) == 1

    def test_delete_record_removes_from_index(self, db):
        db.create_index("first_name")

        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Иван", "Сидоров", 25, "M")

        records = db.select_record(first_name="Иван")
        assert len(records) == 2

        db.delete_record(1)

        records = db.select_record(first_name="Иван")
        assert len(records) == 1
        assert records[0][0] == 2

    def test_select_by_id_using_index(self, db):
        db.create_index("id")
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        records = db.select_record(student_id=1)
        assert len(records) == 1
        assert records[0][1] == "Иван"

    def test_select_by_sex_using_index(self, db):
        db.create_index("sex")
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        db.create_record(3, "Петр", "Сидоров", 25, "M")

        records = db.select_record(sex="M")
        assert len(records) == 2


class TestCSVDatabase:
    """Тесты для CSV БД (без индексов)."""

    @pytest.fixture
    def db_path(self, tmp_path):
        return str(tmp_path / "test_db.csv")

    @pytest.fixture
    def db(self, db_path):
        db = CSVDatabase(db_path)
        db.clear()
        return db

    def test_create_and_persist(self, db_path):
        db1 = CSVDatabase(db_path)
        db1.create_record(1, "Иван", "Петров", 20, "M")

        db2 = CSVDatabase(db_path)
        records = db2.get_all_records()
        assert len(records) == 1

    def test_select_by_filter(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        records = db.select_record(sex="F")
        assert len(records) == 1
        assert records[0][1] == "Мария"

    def test_update_record(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.update_record(1, age=25)

        records = db.select_record(student_id=1)
        assert records[0][3] == 25

    def test_delete_record(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.delete_record(1)

        assert len(db.get_all_records()) == 0

    def test_sort_records(self, db):
        db.create_record(1, "Иван", "Петров", 30, "M")
        db.create_record(2, "Мария", "Иванова", 20, "F")

        sorted_records = db.sort_records("age")
        assert sorted_records[0][3] == 20
        assert sorted_records[1][3] == 30

    def test_update_record_nonexistent(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        result = db.update_record(999, age=25)
        assert result is None

    def test_update_record_age_negative(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        with pytest.raises(InvalidAgeError):
            db.update_record(1, age=-5)

    def test_select_by_id(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        records = db.select_record(student_id=2)
        assert len(records) == 1
        assert records[0][1] == "Мария"

    def test_select_by_name(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        records = db.select_record(first_name="Иван")
        assert len(records) == 1
        assert records[0][0] == 1

    def test_select_multiple_filters(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Иван", "Сидоров", 25, "M")
        db.create_record(3, "Петр", "Петров", 30, "M")

        records = db.select_record(first_name="Иван", second_name="Петров")
        assert len(records) == 1
        assert records[0][0] == 1

    def test_clear_database(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        assert len(db.get_all_records()) == 2
        db.clear()
        assert len(db.get_all_records()) == 0

    def test_sort_by_name_desc(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Анна", "Иванова", 22, "F")
        db.create_record(3, "Борис", "Сидоров", 25, "M")

        sorted_records = db.sort_records("first_name", reverse=True)
        assert sorted_records[0][1] == "Иван"
        assert sorted_records[1][1] == "Борис"
        assert sorted_records[2][1] == "Анна"

    def test_sort_by_age_desc(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 30, "F")
        db.create_record(3, "Петр", "Сидоров", 25, "M")

        sorted_records = db.sort_records("age", reverse=True)
        assert sorted_records[0][3] == 30
        assert sorted_records[1][3] == 25
        assert sorted_records[2][3] == 20

    def test_get_all_records_empty(self, db):
        records = db.get_all_records()
        assert records == []

    def test_get_all_records_with_data(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")

        records = db.get_all_records()
        assert len(records) == 2


    class TestJSONDatabaseFullCoverage:
        """Тесты для полного покрытия JSON БД."""

        def test_create_duplicate_id(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            with pytest.raises(DuplicateIDError):
                db.create_record(1, "Петр", "Сидоров", 25, "M")

        def test_create_negative_age(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            with pytest.raises(InvalidAgeError):
                db.create_record(1, "Иван", "Петров", -5, "M")

        def test_update_negative_age(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            with pytest.raises(InvalidAgeError):
                db.update_record(1, age=-5)

        def test_select_with_all_filters(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record(student_id=1, first_name="Иван",
                                       second_name="Петров", age=20, sex="M")
            assert len(records) == 1

        def test_select_no_filters(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            records = db.select_record()
            assert len(records) == 1

        def test_select_with_empty_strings(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            records = db.select_record(first_name="", second_name="", sex="")
            assert len(records) == 1

        def test_delete_nonexistent(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            result = db.delete_record(999)
            assert result is False

        def test_update_nonexistent(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            result = db.update_record(999, age=25)
            assert result is None

        def test_json_database_update_partial(self, tmp_path):
            """Тест частичного обновления JSON БД."""
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            # Обновляем только имя
            updated = db.update_record(1, first_name="Петр")
            assert updated[1] == "Петр"
            assert updated[2] == "Петров"  # Фамилия не изменилась

            # Обновляем только фамилию
            updated = db.update_record(1, second_name="Сидоров")
            assert updated[2] == "Сидоров"

            # Обновляем только возраст
            updated = db.update_record(1, age=25)
            assert updated[3] == 25

            # Обновляем только пол
            updated = db.update_record(1, sex="F")
            assert updated[4] == "F"

        def test_csv_database_complete_coverage(self, tmp_path):
            """Тест полного покрытия CSV БД."""
            db_path = str(tmp_path / "test.csv")
            db = CSVDatabase(db_path)
            db.clear()

            # create_record
            db.create_record(1, "Тест", "Тестов", 20, "M")

            # select_record разные варианты
            records = db.select_record(student_id=1)
            assert len(records) == 1

            records = db.select_record(first_name="Тест")
            assert len(records) == 1

            records = db.select_record(second_name="Тестов")
            assert len(records) == 1

            records = db.select_record(age=20)
            assert len(records) == 1

            records = db.select_record(sex="M")
            assert len(records) == 1

            records = db.select_record(first_name="", second_name="", sex="")
            assert len(records) == 1

            # update_record
            updated = db.update_record(1, age=25)
            assert updated[3] == 25

            # update_record not found
            result = db.update_record(999, age=30)
            assert result is None

            # delete_record not found
            result = db.delete_record(999)
            assert result is False

            # sort_records
            db.create_record(2, "B", "Второй", 30, "M")
            db.create_record(3, "C", "Третий", 10, "F")

            sorted_records = db.sort_records("age")
            assert sorted_records[0][3] == 10

            sorted_records = db.sort_records("id", reverse=True)
            assert sorted_records[0][0] == 3

    class TestJSONFullCoverage:
        """Полное покрытие JSON БД."""

        def test_select_with_empty_filters(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            records = db.select_record(first_name="", second_name="", sex="")
            assert len(records) == 1

        def test_select_no_filters_full(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record()
            assert len(records) == 2

        def test_update_all_fields(self, tmp_path):
            db_path = str(tmp_path / "test.json")
            db = JSONDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            updated = db.update_record(1, first_name="Петр", second_name="Сидоров", age=25, sex="F")
            assert updated[1] == "Петр"
            assert updated[2] == "Сидоров"
            assert updated[3] == 25
            assert updated[4] == "F"

        def test_save_and_load_persistence(self, tmp_path):
            db_path = str(tmp_path / "test.json")

            # Первая БД - создаём данные
            db1 = JSONDatabase(db_path)
            db1.clear()
            db1.create_record(1, "Иван", "Петров", 20, "M")
            db1.create_record(2, "Мария", "Иванова", 22, "F")

            # Вторая БД - загружаем те же данные
            db2 = JSONDatabase(db_path)
            records = db2.get_all_records()
            assert len(records) == 2

    class TestCSVFullCoverage:
        """Полное покрытие CSV БД."""

        def test_csv_select_all_filters(self, tmp_path):
            db_path = str(tmp_path / "test.csv")
            db = CSVDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record()
            assert len(records) == 2

        def test_csv_select_by_lastname(self, tmp_path):
            db_path = str(tmp_path / "test.csv")
            db = CSVDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.select_record(second_name="Петров")
            assert len(records) == 1
            assert records[0][1] == "Иван"

        def test_csv_update_all_fields(self, tmp_path):
            db_path = str(tmp_path / "test.csv")
            db = CSVDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            updated = db.update_record(1, first_name="Петр", second_name="Сидоров", age=25, sex="F")
            assert updated[1] == "Петр"
            assert updated[2] == "Сидоров"
            assert updated[3] == 25
            assert updated[4] == "F"

        def test_csv_sort_by_lastname(self, tmp_path):
            db_path = str(tmp_path / "test.csv")
            db = CSVDatabase(db_path)
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Анна", "Андреева", 22, "F")

            sorted_records = db.sort_records("second_name")
            assert sorted_records[0][2] == "Андреева"
            assert sorted_records[1][2] == "Петров"