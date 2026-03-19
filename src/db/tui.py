from typing import Optional, List, Tuple
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class StudentTUI:

    def __init__(self) -> None:
        """Инициализация TUI с таблицей студентов."""
        self.student_table = StudentTable()
        self.running = False

    def run(self) -> None:
        """Запускает основной цикл текстового пользовательского интерфейса."""
        self.running = True
        while self.running:
            self._print_menu()
            action = self._get_user_input("Выберите действие: ")
            self._handle_action(action)

    def _print_menu(self) -> None:
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("6. Сортировать записи")
        print("0. Выход")

    def _get_user_input(self, prompt: str) -> str:
        """Получает ввод пользователя."""
        return input(prompt).strip()

    def _read_int(self, prompt: str) -> int:
        """Читает целочисленное значение из консоли."""
        raw = self._get_user_input(prompt)
        try:
            return int(raw)
        except ValueError:
            raise ValueError("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> Optional[int]:
        """Читает необязательное целочисленное значение."""
        raw = self._get_user_input(prompt)
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")
            return self._read_optional_int(prompt)

    def _read_string_optional(self, prompt: str) -> Optional[str]:
        """Читает необязательное строковое значение."""
        value = self._get_user_input(prompt)
        return value if value else None

    def _print_records(self, records: List[Tuple[int, str, str, int, str]]) -> None:
        """Выводит список записей."""
        if not records:
            print("Записи не найдены.")
            return

        print(f"\nНайдено записей: {len(records)}")
        for record in records:
            print(f"ID: {record[0]}, Имя: {record[1]}, Фамилия: {record[2]}, "
                  f"Возраст: {record[3]}, Пол: {record[4]}")

    def _add_student(self) -> None:
        """Добавляет новую запись."""
        print("\n--- Добавление записи ---")
        try:
            student_id = self._read_int("ID: ")
            first_name = self._get_user_input("Имя: ")
            second_name = self._get_user_input("Фамилия: ")
            age = self._read_int("Возраст: ")
            sex = self._get_user_input("Пол (M/F): ")

            record = self.student_table.create_record(
                student_id, first_name, second_name, age, sex
            )
            print(f"✓ Запись добавлена: {record}")
        except (InvalidAgeError, DuplicateIDError) as e:
            print(f"✗ Ошибка: {e}")

    def _show_all_students(self) -> None:
        """Показывает все записи."""
        print("\n--- Все записи ---")
        records = self.student_table.select_record()
        self._print_records(records)

    def _find_students_by_filter(self) -> None:
        """Ищет записи по фильтру."""
        print("\n--- Поиск по фильтру ---")
        print("(Оставьте поле пустым, чтобы пропустить)")

        try:
            student_id = self._read_optional_int("ID: ")
            first_name = self._read_string_optional("Имя: ")
            second_name = self._read_string_optional("Фамилия: ")
            age = self._read_optional_int("Возраст: ")
            sex = self._read_string_optional("Пол (M/F): ")

            records = self.student_table.select_record(
                student_id=student_id,
                first_name=first_name,
                second_name=second_name,
                age=age,
                sex=sex,
            )
            self._print_records(records)
        except ValueError as e:
            print(f"✗ Ошибка: {e}")

    def _update_student(self) -> None:
        """Обновляет запись."""
        print("\n--- Обновление записи ---")
        try:
            student_id = self._read_int("ID записи для обновления: ")
            existing = self.student_table.select_record(student_id=student_id)
            if not existing:
                print(f"✗ Запись с ID={student_id} не найдена")
                return

            print("Текущие данные:", existing[0])
            print("(Оставьте поле пустым, чтобы не менять)")

            first_name = self._read_string_optional("Новое имя: ")
            second_name = self._read_string_optional("Новая фамилия: ")
            age = self._read_optional_int("Новый возраст: ")
            sex = self._read_string_optional("Новый пол (M/F): ")

            updated = self.student_table.update_record(
                student_id, first_name, second_name, age, sex
            )

            if updated:
                print(f"✓ Запись обновлена: {updated}")
            else:
                print("✗ Не удалось обновить запись")
        except InvalidAgeError as e:
            print(f"✗ Ошибка: {e}")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")

    def _delete_student(self) -> None:
        """Удаляет запись."""
        print("\n--- Удаление записи ---")
        try:
            student_id = self._read_int("ID записи для удаления: ")
            existing = self.student_table.select_record(student_id=student_id)
            if not existing:
                print(f"✗ Запись с ID={student_id} не найдена")
                return

            print("Запись для удаления:", existing[0])
            confirm = self._get_user_input("Вы уверены? (д/н): ").lower()

            if confirm in ('д', 'yes', 'y', 'да'):
                deleted = self.student_table.delete_record(student_id)
                if deleted:
                    print(f"✓ Запись с ID={student_id} удалена")
                else:
                    print("✗ Не удалось удалить запись")
            else:
                print("Удаление отменено")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")

    def _sort_students(self) -> None:
        """Сортирует записи."""
        print("\n--- Сортировка записей ---")
        print("Доступные поля для сортировки:")
        print("1. ID")
        print("2. Имя (first_name)")
        print("3. Фамилия (second_name)")
        print("4. Возраст (age)")
        print("5. Пол (sex)")

        field_choice = self._get_user_input("Выберите поле (1-5): ")

        field_map = {
            '1': 'id',
            '2': 'first_name',
            '3': 'second_name',
            '4': 'age',
            '5': 'sex'
        }

        if field_choice not in field_map:
            print("✗ Неверный выбор поля")
            return

        order = self._get_user_input("Порядок (1 - по возрастанию, 2 - по убыванию): ")
        reverse = (order == '2')

        try:
            all_records = self.student_table.select_record()

            if not all_records:
                print("Нет записей для сортировки")
                return

            field_index = {
                'id': 0,
                'first_name': 1,
                'second_name': 2,
                'age': 3,
                'sex': 4
            }[field_map[field_choice]]

            sorted_records = sorted(all_records,
                                    key=lambda record: record[field_index],
                                    reverse=reverse)

            print(f"\n✓ Отсортировано по полю '{field_map[field_choice]}' " +
                  f"({'по возрастанию' if not reverse else 'по убыванию'}):")
            self._print_records(sorted_records)

        except Exception as e:
            print(f"✗ Ошибка при сортировке: {e}")

    def _handle_action(self, action: str) -> None:
        """Обрабатывает выбранное пользователем действие."""
        actions = {
            "1": self._add_student,
            "2": self._show_all_students,
            "3": self._find_students_by_filter,
            "4": self._update_student,
            "5": self._delete_student,
            "6": self._sort_students,
            "0": self._exit_program,
        }

        handler = actions.get(action)
        if handler:
            try:
                handler()
            except (InvalidAgeError, DuplicateIDError) as e:
                print(f"✗ Ошибка базы данных: {e}")
            except ValueError as e:
                print(f"✗ Ошибка ввода: {e}")
            except Exception as e:
                print(f"✗ Непредвиденная ошибка: {e}")
        else:
            print("Неизвестная команда. Повторите ввод.")

    def _exit_program(self) -> None:
        """Завершает работу программы."""
        print("Выход из программы.")
        self.running = False


def run() -> None:
    """Запускает текстовый пользовательский интерфейс."""
    tui = StudentTUI()
    tui.run()


if __name__ == "__main__":
    run()