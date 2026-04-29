import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from src.db.tui import StudentTUI, run
from src.db.backend.errors import InvalidAgeError, DuplicateIDError, InvalidSortFieldError


class TestStudentTUI(unittest.TestCase):
    """Тесты для класса StudentTUI."""

    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.tui = StudentTUI()
        # Заменяем реальную таблицу на mock
        self.tui.student_table = MagicMock()

    def test_initialization(self):
        """Тест инициализации TUI."""
        self.assertIsNotNone(self.tui.student_table)
        self.assertFalse(self.tui.running)

    @patch('builtins.input')
    def test_get_user_input(self, mock_input):
        """Тест получения пользовательского ввода."""
        mock_input.return_value = "  test  "
        result = self.tui._get_user_input("Prompt: ")
        self.assertEqual(result, "test")

    @patch('builtins.input')
    def test_read_int_valid(self, mock_input):
        """Тест чтения целого числа (валидный ввод)."""
        mock_input.return_value = "42"
        result = self.tui._read_int("Age: ")
        self.assertEqual(result, 42)

    @patch('builtins.input')
    def test_read_int_invalid(self, mock_input):
        """Тест чтения целого числа (невалидный ввод)."""
        mock_input.return_value = "abc"
        with self.assertRaises(ValueError):
            self.tui._read_int("Age: ")

    @patch('builtins.input')
    def test_read_optional_int_empty(self, mock_input):
        """Тест чтения опционального целого числа (пустой ввод)."""
        mock_input.return_value = ""
        result = self.tui._read_optional_int("Age: ")
        self.assertIsNone(result)

    @patch('builtins.input')
    def test_read_optional_int_valid(self, mock_input):
        """Тест чтения опционального целого числа (валидный ввод)."""
        mock_input.return_value = "42"
        result = self.tui._read_optional_int("Age: ")
        self.assertEqual(result, 42)

    @patch('builtins.input')
    def test_read_string_optional_empty(self, mock_input):
        """Тест чтения опциональной строки (пустой ввод)."""
        mock_input.return_value = ""
        result = self.tui._read_string_optional("Name: ")
        self.assertIsNone(result)

    @patch('builtins.input')
    def test_read_string_optional_valid(self, mock_input):
        """Тест чтения опциональной строки (валидный ввод)."""
        mock_input.return_value = "John"
        result = self.tui._read_string_optional("Name: ")
        self.assertEqual(result, "John")

    def test_print_records_empty(self):
        """Тест вывода пустого списка записей."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._print_records([])
            output = fake_out.getvalue().strip()
            self.assertIn("Записи не найдены", output)

    def test_print_records_non_empty(self):
        """Тест вывода непустого списка записей."""
        records = [(1, "John", "Doe", 20, "M")]
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._print_records(records)
            output = fake_out.getvalue().strip()
            self.assertIn("Найдено записей: 1", output)
            self.assertIn("ID: 1", output)

    @patch('builtins.input')
    def test_add_student_success(self, mock_input):
        """Тест успешного добавления студента."""
        mock_input.side_effect = ["1", "John", "Doe", "20", "M"]
        expected_record = (1, "John", "Doe", 20, "M")
        self.tui.student_table.create_record.return_value = expected_record

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._add_student()
            output = fake_out.getvalue().strip()
            self.assertIn("Запись добавлена", output)

        self.tui.student_table.create_record.assert_called_once_with(1, "John", "Doe", 20, "M")

    @patch('builtins.input')
    def test_add_student_duplicate_id(self, mock_input):
        """Тест добавления студента с дублирующимся ID."""
        mock_input.side_effect = ["1", "Jane", "Smith", "22", "F"]
        self.tui.student_table.create_record.side_effect = DuplicateIDError("Запись с id=1 уже существует.")

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._add_student()
            output = fake_out.getvalue().strip()
            self.assertIn("Ошибка", output)

    @patch('builtins.input')
    def test_add_student_invalid_age(self, mock_input):
        """Тест добавления студента с невалидным возрастом."""
        mock_input.side_effect = ["1", "John", "Doe", "-5", "M"]
        self.tui.student_table.create_record.side_effect = InvalidAgeError("Поле age не может быть отрицательным.")

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._add_student()
            output = fake_out.getvalue().strip()
            self.assertIn("Ошибка", output)

    def test_show_all_students_empty(self):
        """Тест показа всех записей (пустая таблица)."""
        self.tui.student_table.select_record.return_value = []

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._show_all_students()
            output = fake_out.getvalue().strip()
            self.assertIn("Записи не найдены", output)

    def test_show_all_students_non_empty(self):
        """Тест показа всех записей (непустая таблица)."""
        mock_records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        self.tui.student_table.select_record.return_value = mock_records

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._show_all_students()
            output = fake_out.getvalue().strip()
            self.assertIn("Найдено записей: 2", output)
            self.assertIn("John", output)
            self.assertIn("Jane", output)

    def test_sort_students_empty_table(self):
        """Тест сортировки при пустой таблице."""
        self.tui.student_table.sort_records.return_value = []

        with patch('builtins.input', side_effect=["1", "1"]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.tui._sort_students()
                output = fake_out.getvalue().strip()
                self.assertIn("Нет записей для сортировки", output)

    def test_sort_students_invalid_field(self):
        """Тест сортировки с неверным выбором поля."""
        with patch('builtins.input', side_effect=["6", "1"]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.tui._sort_students()
                output = fake_out.getvalue().strip()
                self.assertIn("Неверный выбор поля", output)

    def test_sort_students_success(self):
        """Тест успешной сортировки."""
        mock_records = [(3, "Charlie", "Brown", 22, "M"), (1, "Alice", "Smith", 20, "F")]
        self.tui.student_table.sort_records.return_value = mock_records

        with patch('builtins.input', side_effect=["1", "1"]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.tui._sort_students()
                output = fake_out.getvalue().strip()
                self.assertIn("Отсортировано", output)

        self.tui.student_table.sort_records.assert_called_once_with(key='id', reverse=False)

    def test_read_optional_int_with_invalid_then_valid(self):
        """Тест чтения опционального числа с неверным вводом, затем верным."""
        with patch('builtins.input', side_effect=["abc", "42"]):
            result = self.tui._read_optional_int("Age: ")
            self.assertEqual(result, 42)

    def test_handle_action_with_database_error(self):
        """Тест обработки действия с ошибкой базы данных."""
        tui = StudentTUI()
        tui.student_table = MagicMock()

        def mock_add():
            raise InvalidAgeError("Test error")

        tui._add_student = mock_add

        with patch('sys.stdout', new=StringIO()) as fake_out:
            tui._handle_action("1")
            output = fake_out.getvalue().strip()
            self.assertIn("Ошибка базы данных", output)

    @patch('builtins.input')
    def test_find_students_by_filter(self, mock_input):
        """Тест поиска студентов по фильтру."""
        mock_input.side_effect = ["", "John", "", "", ""]
        mock_records = [(1, "John", "Doe", 20, "M"), (3, "John", "Smith", 20, "M")]
        self.tui.student_table.select_record.return_value = mock_records

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._find_students_by_filter()
            output = fake_out.getvalue().strip()
            self.assertIn("Найдено записей: 2", output)

        self.tui.student_table.select_record.assert_called_once_with(
            student_id=None, first_name="John", second_name=None, age=None, sex=None
        )

    @patch('builtins.input')
    def test_update_student_success(self, mock_input):
        """Тест успешного обновления студента."""
        mock_input.side_effect = ["1", "Johnny", "", "21", ""]
        self.tui.student_table.select_record.return_value = [(1, "John", "Doe", 20, "M")]
        self.tui.student_table.update_record.return_value = (1, "Johnny", "Doe", 21, "M")

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._update_student()
            output = fake_out.getvalue().strip()
            self.assertIn("Запись обновлена", output)

        self.tui.student_table.update_record.assert_called_once_with(1, "Johnny", None, 21, None)

    @patch('builtins.input')
    def test_update_student_not_found(self, mock_input):
        """Тест обновления несуществующего студента."""
        mock_input.side_effect = ["999"]
        self.tui.student_table.select_record.return_value = []

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._update_student()
            output = fake_out.getvalue().strip()
            self.assertIn("не найдена", output)

    @patch('builtins.input')
    def test_delete_student_success(self, mock_input):
        """Тест успешного удаления студента."""
        mock_input.side_effect = ["1", "д"]
        self.tui.student_table.select_record.return_value = [(1, "John", "Doe", 20, "M")]
        self.tui.student_table.delete_record.return_value = True

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._delete_student()
            output = fake_out.getvalue().strip()
            self.assertIn("удалена", output)

        self.tui.student_table.delete_record.assert_called_once_with(1)

    @patch('builtins.input')
    def test_delete_student_cancelled(self, mock_input):
        """Тест отмены удаления студента."""
        mock_input.side_effect = ["1", "н"]
        self.tui.student_table.select_record.return_value = [(1, "John", "Doe", 20, "M")]

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._delete_student()
            output = fake_out.getvalue().strip()
            self.assertIn("Удаление отменено", output)

        self.tui.student_table.delete_record.assert_not_called()

    @patch('builtins.input')
    def test_handle_action_valid(self, mock_input):
        """Тест обработки валидных действий."""
        with patch.object(self.tui, '_exit_program') as mock_exit:
            self.tui._handle_action("0")
            mock_exit.assert_called_once()

    @patch('builtins.input')
    def test_handle_action_invalid(self, mock_input):
        """Тест обработки невалидного действия."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._handle_action("99")
            output = fake_out.getvalue().strip()
            self.assertIn("Неизвестная команда", output)

    @patch('builtins.input')
    def test_run_exit(self, mock_input):
        """Тест запуска и выхода из программы."""
        mock_input.side_effect = ["0"]

        with patch('sys.stdout', new=StringIO()):
            self.tui.run()

        self.assertFalse(self.tui.running)

    def test_exit_program(self):
        """Тест выхода из программы."""
        self.tui.running = True
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.tui._exit_program()
            output = fake_out.getvalue().strip()
            self.assertIn("Выход из программы", output)

        self.assertFalse(self.tui.running)

    @patch('src.db.tui.StudentTUI')
    def test_run_function(self, mock_tui_class):
        """Тест функции run для обратной совместимости."""
        mock_tui_instance = MagicMock()
        mock_tui_class.return_value = mock_tui_instance

        run()

        mock_tui_class.assert_called_once()
        mock_tui_instance.run.assert_called_once()


if __name__ == '__main__':
    unittest.main()