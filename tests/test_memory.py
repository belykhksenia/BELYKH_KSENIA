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

    def test_create_record_negative_age(self, db):
        with pytest.raises(InvalidAgeError):
            db.create_record(1, "Иван", "Петров", -5, "M")

    def test_create_record_duplicate_id(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        with pytest.raises(DuplicateIDError):
            db.create_record(1, "Петр", "Сидоров", 25, "M")

    def test_select_all(self, db):
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

    def test_select_by_filter(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.create_record(2, "Мария", "Иванова", 22, "F")
        records = db.select_record(sex="F")
        assert len(records) == 1
        assert records[0][1] == "Мария"

    def test_update_record(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        updated = db.update_record(1, age=21)
        assert updated[3] == 21

    def test_update_nonexistent(self, db):
        result = db.update_record(999, age=21)
        assert result is None

    def test_delete_record(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        assert db.delete_record(1) == True
        assert len(db.get_all_records()) == 0

    def test_delete_nonexistent(self, db):
        assert db.delete_record(999) == False

    def test_sort_by_age(self, db):
        db.create_record(1, "Иван", "Петров", 30, "M")
        db.create_record(2, "Мария", "Иванова", 20, "F")
        db.create_record(3, "Петр", "Сидоров", 25, "M")

        sorted_records = db.sort_records("age", reverse=False)
        assert sorted_records[0][3] == 20
        assert sorted_records[1][3] == 25
        assert sorted_records[2][3] == 30

    def test_sort_invalid_field(self, db):
        with pytest.raises(InvalidSortFieldError):
            db.sort_records("invalid_field")

    def test_clear(self, db):
        db.create_record(1, "Иван", "Петров", 20, "M")
        db.clear()
        assert len(db.get_all_records()) == 0


    def test_update_record_age_negative(self, db):
            """Тест обновления с отрицательным возрастом."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            with pytest.raises(InvalidAgeError, match="Поле age не может быть отрицательным"):
                db.update_record(1, age=-5)

    def test_update_record_nonexistent_id(self, db):
            """Тест обновления несуществующего ID."""
            result = db.update_record(999, age=25)
            assert result is None

    def test_delete_record_nonexistent_id(self, db):
            """Тест удаления несуществующего ID."""
            result = db.delete_record(999)
            assert result is False

    def test_sort_by_id_ascending(self, db):
            """Тест сортировки по ID по возрастанию."""
            db.create_record(3, "Петр", "Сидоров", 25, "M")
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            sorted_records = db.sort_records("id", reverse=False)
            assert sorted_records[0][0] == 1
            assert sorted_records[1][0] == 2
            assert sorted_records[2][0] == 3

    def test_sort_by_id_descending(self, db):
            """Тест сортировки по ID по убыванию."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")
            db.create_record(3, "Петр", "Сидоров", 25, "M")

            sorted_records = db.sort_records("id", reverse=True)
            assert sorted_records[0][0] == 3
            assert sorted_records[1][0] == 2
            assert sorted_records[2][0] == 1

    def test_sort_by_name(self, db):
            """Тест сортировки по имени."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Анна", "Иванова", 22, "F")
            db.create_record(3, "Борис", "Сидоров", 25, "M")

            sorted_records = db.sort_records("first_name", reverse=False)
            assert sorted_records[0][1] == "Анна"
            assert sorted_records[1][1] == "Борис"
            assert sorted_records[2][1] == "Иван"

    def test_get_all_records_after_operations(self, db):
            """Тест получения записей после операций."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")

            records = db.get_all_records()
            assert len(records) == 2

            db.delete_record(1)
            records = db.get_all_records()
            assert len(records) == 1
            assert records[0][0] == 2

    def test_select_with_multiple_filters(self, db):
            """Тест выбора с несколькими фильтрами."""
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Иван", "Сидоров", 25, "M")
            db.create_record(3, "Петр", "Петров", 30, "M")

            records = db.select_record(first_name="Иван", second_name="Петров")
            assert len(records) == 1
            assert records[0][0] == 1

            # Добавьте в конец файла test_memory.py

    def test_database_interface_methods(self, db):
        """Тест всех методов интерфейса."""
        # Создание записи
        record = db.create_record(1, "Иван", "Петров", 20, "M")
        assert record is not None

        # Выборка
        records = db.select_record()
        assert len(records) == 1

        # Выборка с фильтрами
        records = db.select_record(first_name="Иван")
        assert len(records) == 1

        # Обновление
        updated = db.update_record(1, age=21)
        assert updated[3] == 21

        # Получение всех
        all_records = db.get_all_records()
        assert len(all_records) == 1

        # Сортировка
        sorted_records = db.sort_records("id")
        assert len(sorted_records) == 1

        # Удаление
        result = db.delete_record(1)
        assert result is True

        # Очистка
        db.clear()
        assert len(db.get_all_records()) == 0

    def test_abstract_interface_methods(self, db):
        """Тест всех абстрактных методов через конкретную реализацию."""
        # create_record
        record = db.create_record(100, "Абстракт", "Тест", 25, "M")
        assert record[0] == 100

        # select_record
        records = db.select_record(student_id=100)
        assert len(records) == 1

        # select_record with all params
        records = db.select_record(student_id=100, first_name="Абстракт",
                                   second_name="Тест", age=25, sex="M")
        assert len(records) == 1

        # select_record with empty strings
        records = db.select_record(first_name="", second_name="", sex="")
        assert len(records) >= 1

        # update_record
        updated = db.update_record(100, age=26)
        assert updated[3] == 26

        # update_record not found
        result = db.update_record(999, age=30)
        assert result is None

        # get_all_records
        all_records = db.get_all_records()
        assert len(all_records) >= 1

        # delete_record
        deleted = db.delete_record(100)
        assert deleted is True

        # delete_record not found
        deleted = db.delete_record(999)
        assert deleted is False

        # clear
        db.clear()
        assert len(db.get_all_records()) == 0

        # Добавьте эти тесты в конец файла test_memory.py

        def test_database_interface_complete(self, db):
            """Полное тестирование интерфейса database.py."""
            # create_record
            record = db.create_record(100, "Интерфейс", "Тест", 25, "M")
            assert record[0] == 100

            # select_record with all parameters
            records = db.select_record(student_id=100, first_name="Интерфейс",
                                       second_name="Тест", age=25, sex="M")
            assert len(records) == 1

            # select_record with empty strings
            records = db.select_record(first_name="", second_name="", sex="")
            assert len(records) >= 1

            # select_record with None
            records = db.select_record(student_id=None, first_name=None)
            assert len(records) >= 1

            # update_record
            updated = db.update_record(100, age=26)
            assert updated[3] == 26

            # update_record with partial data
            updated = db.update_record(100, first_name="Обновлено")
            assert updated[1] == "Обновлено"

            # update_record not found
            result = db.update_record(999, age=30)
            assert result is None

            # get_all_records
            all_records = db.get_all_records()
            assert len(all_records) >= 1

            # delete_record
            deleted = db.delete_record(100)
            assert deleted is True

            # delete_record not found
            deleted = db.delete_record(999)
            assert deleted is False

            # sort_records
            db.create_record(3, "Z", "Last", 30, "M")
            db.create_record(1, "A", "First", 10, "F")
            sorted_records = db.sort_records("id")
            assert sorted_records[0][0] == 1
            assert sorted_records[1][0] == 3

            # sort_records reverse
            sorted_records = db.sort_records("id", reverse=True)
            assert sorted_records[0][0] == 3
            assert sorted_records[1][0] == 1

            # clear
            db.clear()
            assert len(db.get_all_records()) == 0

        def test_database_abstract_methods_coverage(self, db):
            """Тест для покрытия абстрактных методов database.py."""
            # Создаём запись для теста
            record = db.create_record(999, "Покрытие", "Тест", 25, "M")
            assert record[0] == 999

            # select_record с разными комбинациями параметров
            # Покрываем строки 15, 22, 29, 34, 39, 44, 49 в database.py
            records = db.select_record(student_id=999)
            assert len(records) == 1

            records = db.select_record(first_name="Покрытие")
            assert len(records) == 1

            records = db.select_record(second_name="Тест")
            assert len(records) == 1

            records = db.select_record(age=25)
            assert len(records) == 1

            records = db.select_record(sex="M")
            assert len(records) == 1

            # update_record
            updated = db.update_record(999, age=26)
            assert updated[3] == 26

            # update_record с частичными данными
            updated = db.update_record(999, first_name="Новое")
            assert updated[1] == "Новое"

            # delete_record
            deleted = db.delete_record(999)
            assert deleted is True

            # delete_record несуществующий
            deleted = db.delete_record(888)
            assert deleted is False

            # sort_records по разным полям
            db.clear()
            db.create_record(3, "C", "Третий", 30, "M")
            db.create_record(1, "A", "Первый", 10, "F")
            db.create_record(2, "B", "Второй", 20, "M")

            sorted_by_id = db.sort_records("id")
            assert sorted_by_id[0][0] == 1

            sorted_by_name = db.sort_records("first_name")
            assert sorted_by_name[0][1] == "A"

            sorted_by_age = db.sort_records("age")
            assert sorted_by_age[0][3] == 10

            # get_all_records
            all_records = db.get_all_records()
            assert len(all_records) == 3

            # clear
            db.clear()
            assert len(db.get_all_records()) == 0

        def test_sort_by_sex_field(self, db):
            """Тест сортировки по полу."""
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Мария", "Иванова", 22, "F")
            db.create_record(3, "Анна", "Сидорова", 25, "F")

            sorted_records = db.sort_records("sex")
            # F (женщины) должны быть первыми (по алфавиту F < M)
            assert sorted_records[0][4] == "F"

        def test_sort_by_first_name_desc(self, db):
            """Тест сортировки по имени по убыванию."""
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")
            db.create_record(2, "Анна", "Иванова", 22, "F")
            db.create_record(3, "Борис", "Сидоров", 25, "M")

            sorted_records = db.sort_records("first_name", reverse=True)
            assert sorted_records[0][1] == "Иван"  # Иван > Борис > Анна

        def test_get_all_records_empty_db(self, db):
            """Тест получения записей из пустой БД."""
            db.clear()
            records = db.get_all_records()
            assert records == []

        def test_select_with_none_values(self, db):
            """Тест выборки с None значениями."""
            db.clear()
            db.create_record(1, "Иван", "Петров", 20, "M")

            # Все параметры None - должны вернуть все записи
            records = db.select_record(student_id=None, first_name=None,
                                       second_name=None, age=None, sex=None)
            assert len(records) == 1