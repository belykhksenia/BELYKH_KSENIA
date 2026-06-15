"""Тесты для текстового пользовательского интерфейса."""

import pytest
from unittest.mock import patch
import os
import tempfile

from src.db.tui import StudentTUI
from src.db.backend import (
    MemoryDatabase, JSONDatabase, CSVDatabase,
    InvalidAgeError, DuplicateIDError, InvalidSortFieldError
)


class TestStudentTUI:
    """Тесты для StudentTUI."""

    @pytest.fixture
    def tui(self):
        """Создание TUI с memory БД для тестов."""
        tui = StudentTUI(db_type="memory", db_path="data/test_db")
        tui.database.clear()
        return tui

    @pytest.fixture
    def tui_json(self):
        """Создание TUI с JSON БД для тестов."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_db")
        tui = StudentTUI(db_type="json", db_path=db_path)
        tui.database.clear()
        return tui

    @pytest.fixture
    def tui_csv(self):
        """Создание TUI с CSV БД для тестов."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_db")
        tui = StudentTUI(db_type="csv", db_path=db_path)
        tui.database.clear()
        return tui

    # === Тесты инициализации ===

    def test_init_memory(self):
        """Тест инициализации с memory БД."""
        tui = StudentTUI(db_type="memory")
        assert tui.db_type == "memory"
        assert isinstance(tui.database, MemoryDatabase)

    def test_init_json(self):
        """Тест инициализации с JSON БД."""
        tui = StudentTUI(db_type="json", db_path="data/test")
        assert tui.db_type == "json"
        assert isinstance(tui.database, JSONDatabase)

    def test_init_csv(self):
        """Тест инициализации с CSV БД."""
        tui = StudentTUI(db_type="csv", db_path="data/test")
        assert tui.db_type == "csv"
        assert isinstance(tui.database, CSVDatabase)

    def test_init_invalid_db_type(self):
        """Тест инициализации с неверным типом БД."""
        with pytest.raises(ValueError, match="Неизвестный тип БД"):
            StudentTUI(db_type="invalid")

    # === Тесты ввода/вывода ===

    @patch('builtins.input')
    def test_get_user_input(self, mock_input, tui):
        """Тест получения пользовательского ввода."""
        mock_input.return_value = "test input"
        result = tui._get_user_input("Prompt: ")
        assert result == "test input"

    @patch('builtins.input')
    def test_read_int_valid(self, mock_input, tui):
        """Тест чтения целого числа."""
        mock_input.return_value = "42"
        result = tui._read_int("Enter number: ")
        assert result == 42

    @patch('builtins.input')
    def test_read_int_invalid(self, mock_input, tui):
        """Тест чтения неверного целого числа."""
        mock_input.return_value = "not a number"
        with pytest.raises(ValueError, match="введите целое число"):
            tui._read_int("Enter number: ")

    @patch('builtins.input')
    def test_read_optional_int_with_value(self, mock_input, tui):
        """Тест чтения опционального целого числа (с значением)."""
        mock_input.return_value = "25"
        result = tui._read_optional_int("Enter age: ")
        assert result == 25

    @patch('builtins.input')
    def test_read_optional_int_empty(self, mock_input, tui):
        """Тест чтения опционального целого числа (пустое значение)."""
        mock_input.return_value = ""
        result = tui._read_optional_int("Enter age: ")
        assert result is None

    @patch('builtins.input')
    def test_read_string_optional_with_value(self, mock_input, tui):
        """Тест чтения опциональной строки (с значением)."""
        mock_input.return_value = "John"
        result = tui._read_string_optional("Enter name: ")
        assert result == "John"

    @patch('builtins.input')
    def test_read_string_optional_empty(self, mock_input, tui):
        """Тест чтения опциональной строки (пустое значение)."""
        mock_input.return_value = ""
        result = tui._read_string_optional("Enter name: ")
        assert result is None

    # === Тесты вывода ===

    def test_print_records_empty(self, tui, capsys):
        """Тест вывода пустого списка записей."""
        tui._print_records([])
        captured = capsys.readouterr()
        assert "Записи не найдены" in captured.out

    def test_print_records_with_data(self, tui, capsys):
        """Тест вывода списка записей."""
        records = [(1, "Иван", "Петров", 20, "M")]
        tui._print_records(records)
        captured = capsys.readouterr()
        assert "Найдено записей: 1" in captured.out
        assert "Иван" in captured.out

    def test_print_menu_memory(self, tui, capsys):
        """Тест вывода меню для memory БД."""
        tui._print_menu()
        captured = capsys.readouterr()
        assert "Добавить запись" in captured.out
        assert "Управление индексами" not in captured.out

    def test_print_menu_json(self, tui_json, capsys):
        """Тест вывода меню для JSON БД."""
        tui_json._print_menu()
        captured = capsys.readouterr()
        assert "Добавить запись" in captured.out
        assert "Управление индексами" in captured.out

    # === Тесты операций ===

    @patch('builtins.input')
    def test_add_student_success(self, mock_input, tui):
        """Тест успешного добавления студента."""
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "M"]
        tui._add_student()
        records = tui.database.get_all_records()
        assert len(records) == 1
        assert records[0][0] == 1
        assert records[0][1] == "Иван"

    @patch('builtins.input')
    def test_add_student_duplicate_id(self, mock_input, tui):
        """Тест добавления дублирующего ID."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        mock_input.side_effect = ["1", "Петр", "Сидоров", "25", "M"]
        with patch('builtins.print') as mock_print:
            tui._add_student()
            assert mock_print.called

    @patch('builtins.input')
    def test_add_student_invalid_age(self, mock_input, tui):
        """Тест добавления с отрицательным возрастом."""
        mock_input.side_effect = ["1", "Иван", "Петров", "-5", "M"]
        with patch('builtins.print') as mock_print:
            tui._add_student()
            assert mock_print.called

    def test_show_all_students_empty(self, tui, capsys):
        """Тест показа всех записей (пустая БД)."""
        tui._show_all_students()
        captured = capsys.readouterr()
        assert "Записи не найдены" in captured.out

    def test_show_all_students_with_data(self, tui, capsys):
        """Тест показа всех записей (с данными)."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        tui._show_all_students()
        captured = capsys.readouterr()
        assert "Иван" in captured.out

    @patch('builtins.input')
    def test_find_students_by_filter_id(self, mock_input, tui, capsys):
        """Тест поиска по ID."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        tui.database.create_record(2, "Мария", "Иванова", 22, "F")
        mock_input.side_effect = ["1", "", "", "", ""]
        tui._find_students_by_filter()
        captured = capsys.readouterr()
        assert "Иван" in captured.out

    @patch('builtins.input')
    def test_find_students_by_filter_sex(self, mock_input, tui, capsys):
        """Тест поиска по полу."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        tui.database.create_record(2, "Мария", "Иванова", 22, "F")
        mock_input.side_effect = ["", "", "", "", "F"]
        tui._find_students_by_filter()
        captured = capsys.readouterr()
        assert "Мария" in captured.out

    @patch('builtins.input')
    def test_update_student_success(self, mock_input, tui):
        """Тест успешного обновления записи."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        mock_input.side_effect = ["1", "", "", "25", ""]
        tui._update_student()
        records = tui.database.select_record(student_id=1)
        assert records[0][3] == 25

    @patch('builtins.input')
    def test_update_student_not_found(self, mock_input, tui):
        """Тест обновления несуществующей записи."""
        mock_input.side_effect = ["999"]
        with patch('builtins.print') as mock_print:
            tui._update_student()
            mock_print.assert_called_with("Запись с ID=999 не найдена")

    @patch('builtins.input')
    def test_delete_student_success(self, mock_input, tui):
        """Тест успешного удаления записи."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        mock_input.side_effect = ["1", "д"]
        tui._delete_student()
        assert len(tui.database.get_all_records()) == 0

    @patch('builtins.input')
    def test_delete_student_cancel(self, mock_input, tui):
        """Тест отмены удаления."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        mock_input.side_effect = ["1", "н"]
        tui._delete_student()
        assert len(tui.database.get_all_records()) == 1

    @patch('builtins.input')
    def test_sort_students_by_age(self, mock_input, tui):
        """Тест сортировки по возрасту."""
        tui.database.create_record(1, "Иван", "Петров", 30, "M")
        tui.database.create_record(2, "Мария", "Иванова", 20, "F")
        mock_input.side_effect = ["4", "1"]
        with patch('builtins.print') as mock_print:
            tui._sort_students()
            assert mock_print.called

    @patch('builtins.input')
    def test_sort_students_invalid_field(self, mock_input, tui, capsys):
        """Тест сортировки с неверным полем."""
        mock_input.side_effect = ["0", "1"]
        tui._sort_students()
        captured = capsys.readouterr()
        assert "Неверный выбор поля" in captured.out

    def test_exit_program(self, tui):
        """Тест выхода из программы."""
        tui._exit_program()
        assert tui.running is False

    @patch('builtins.input')
    def test_handle_action_add(self, mock_input, tui):
        """Тест обработки действия 'добавить'."""
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "M"]
        tui._handle_action("1")
        assert len(tui.database.get_all_records()) == 1

    def test_handle_action_show(self, tui, capsys):
        """Тест обработки действия 'показать все'."""
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        tui._handle_action("2")
        captured = capsys.readouterr()
        assert "Иван" in captured.out

    def test_handle_action_invalid(self, tui, capsys):
        """Тест обработки неверного действия."""
        tui._handle_action("99")
        captured = capsys.readouterr()
        assert "Неизвестная команда" in captured.out

    def test_handle_action_exit(self, tui):
        """Тест обработки действия 'выход'."""
        tui._handle_action("0")
        assert tui.running is False

    # === Тесты индексов ===

    @patch('builtins.input')
    def test_manage_indexes_show(self, mock_input, tui_json, capsys):
        """Тест показа индексов."""
        tui_json.database.create_record(1, "Иван", "Петров", 20, "M")
        tui_json.database.create_index("age")
        mock_input.side_effect = ["1"]
        tui_json._manage_indexes()
        captured = capsys.readouterr()
        assert "age" in captured.out or "индексы" in captured.out.lower()

    @patch('builtins.input')
    def test_manage_indexes_create(self, mock_input, tui_json, capsys):
        """Тест создания индекса."""
        tui_json.database.create_record(10, "Тест", "Тестов", 20, "M")
        mock_input.side_effect = ["2", "4"]
        tui_json._manage_indexes()
        captured = capsys.readouterr()
        assert "создан" in captured.out or "Индекс" in captured.out

    @patch('builtins.input')
    def test_manage_indexes_invalid_choice(self, mock_input, tui_json):
        """Тест неверного выбора в управлении индексами."""
        mock_input.side_effect = ["5"]
        with patch('builtins.print') as mock_print:
            tui_json._manage_indexes()
            assert mock_print.called


class TestTUIIntegration:
    """Интеграционные тесты TUI."""

    @patch('builtins.input')
    def test_full_workflow_memory(self, mock_input):
        """Полный сценарий работы с memory БД."""
        tui = StudentTUI(db_type="memory")
        tui.database.clear()

        mock_input.side_effect = ["1", "Иван", "Петров", "20", "M"]
        tui._add_student()
        assert len(tui.database.get_all_records()) == 1

        mock_input.side_effect = ["1", "", "", "21", ""]
        tui._update_student()
        updated = tui.database.select_record(student_id=1)
        assert updated[0][3] == 21

        mock_input.side_effect = ["1", "д"]
        tui._delete_student()
        assert len(tui.database.get_all_records()) == 0

    def test_full_workflow_json(self):
        """Полный сценарий работы с JSON БД."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_db")

        tui = StudentTUI(db_type="json", db_path=db_path)
        tui.database.clear()
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        tui.database.create_index("age")

        records = tui.database.select_record(age=20)
        assert len(records) == 1

        tui2 = StudentTUI(db_type="json", db_path=db_path)
        assert len(tui2.database.get_all_records()) == 1

    def test_full_workflow_csv(self):
        """Полный сценарий работы с CSV БД."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_db")

        tui = StudentTUI(db_type="csv", db_path=db_path)
        tui.database.clear()
        tui.database.create_record(1, "Иван", "Петров", 20, "M")
        tui.database.create_record(2, "Мария", "Иванова", 22, "F")

        records = tui.database.get_all_records()
        assert len(records) == 2

        found = tui.database.select_record(sex="F")
        assert len(found) == 1
        assert found[0][1] == "Мария"

        tui.database.update_record(1, age=25)
        updated = tui.database.select_record(student_id=1)
        assert updated[0][3] == 25

        tui.database.delete_record(1)
        assert len(tui.database.get_all_records()) == 1

    @patch('builtins.input')
    def test_run_exit(self, mock_input):
        """Тест выхода из главного цикла."""
        mock_input.return_value = "0"
        tui = StudentTUI(db_type="memory")
        with patch('builtins.print'):
            tui.run()
        assert tui.running is False
