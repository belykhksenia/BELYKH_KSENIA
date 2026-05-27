"""Текстовый пользовательский интерфейс для работы с базой данных студентов."""

from typing import Optional, List, Tuple
from src.db.backend import (
    StudentTable, MemoryDatabase, JSONDatabase, CSVDatabase,
    InvalidAgeError, DuplicateIDError, InvalidSortFieldError,
    DatabaseLoadError, DatabaseSaveError
)


class StudentTUI:
    """Текстовый интерфейс для управления базой данных студентов."""

    def __init__(self, db_type: str = "memory", db_path: str = "data/database"):
        """
        Инициализация TUI с выбором типа базы данных.

        Args:
            db_type: Тип БД ('memory', 'json', 'csv')
            db_path: Путь к файлу (без расширения для json/csv)
        """
        self.db_type = db_type
        self.db_path = db_path
        self.database = self._create_database(db_type, db_path)
        self.running = False

    def _create_database(self, db_type: str, db_path: str):
        """Создаёт экземпляр базы данных выбранного типа."""
        if db_type == "memory":
            return MemoryDatabase()
        elif db_type == "json":
            return JSONDatabase(f"{db_path}.json")
        elif db_type == "csv":
            return CSVDatabase(f"{db_path}.csv")
        else:
            raise ValueError(f"Неизвестный тип БД: {db_type}")

    def run(self) -> None:
        """Запускает основной цикл."""
        self.running = True
        print(f"\n=== База данных студентов (тип: {self.db_type.upper()}) ===")

        while self.running:
            self._print_menu()
            action = self._get_user_input("Выберите действие: ")
            self._handle_action(action)

    def _print_menu(self) -> None:
        print("\n=== Меню ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("6. Сортировать записи")

        if self.db_type == "json" and hasattr(self.database, 'create_index'):
            print("7. Управление индексами")

        print("0. Выход")

    def _get_user_input(self, prompt: str) -> str:
        return input(prompt).strip()

    def _read_int(self, prompt: str) -> int:
        raw = self._get_user_input(prompt)
        try:
            return int(raw)
        except ValueError:
            raise ValueError("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> Optional[int]:
        raw = self._get_user_input(prompt)
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")
            return self._read_optional_int(prompt)

    def _read_string_optional(self, prompt: str) -> Optional[str]:
        value = self._get_user_input(prompt)
        return value if value else None

    def _print_records(self, records: List[Tuple[int, str, str, int, str]]) -> None:
        if not records:
            print("Записи не найдены.")
            return

        print(f"\nНайдено записей: {len(records)}")
        print("-" * 70)
        for record in records:
            print(f"ID: {record[0]:3} | Имя: {record[1]:10} | Фамилия: {record[2]:10} | "
                  f"Возраст: {record[3]:3} | Пол: {record[4]}")
        print("-" * 70)

    def _add_student(self) -> None:
        print("\n--- Добавление записи ---")
        try:
            student_id = self._read_int("ID: ")
            first_name = self._get_user_input("Имя: ")
            second_name = self._get_user_input("Фамилия: ")
            age = self._read_int("Возраст: ")
            sex = self._get_user_input("Пол (M/F): ")

            record = self.database.create_record(student_id, first_name, second_name, age, sex)
            print(f"✓ Запись добавлена: {record}")
        except (InvalidAgeError, DuplicateIDError) as e:
            print(f"✗ Ошибка: {e}")

    def _show_all_students(self) -> None:
        print("\n--- Все записи ---")
        records = self.database.get_all_records()
        self._print_records(records)

    def _find_students_by_filter(self) -> None:
        print("\n--- Поиск по фильтру ---")
        print("(Оставьте поле пустым, чтобы пропустить)")

        try:
            student_id = self._read_optional_int("ID: ")
            first_name = self._read_string_optional("Имя: ")
            second_name = self._read_string_optional("Фамилия: ")
            age = self._read_optional_int("Возраст: ")
            sex = self._read_string_optional("Пол (M/F): ")

            records = self.database.select_record(
                student_id=student_id, first_name=first_name,
                second_name=second_name, age=age, sex=sex
            )

            if self.db_type == "json" and hasattr(self.database, 'get_indices'):
                indices = self.database.get_indices()
                if indices:
                    print(f"\n📊 Используются индексы: {list(indices.keys())}")

            self._print_records(records)
        except ValueError as e:
            print(f"✗ Ошибка: {e}")

    def _update_student(self) -> None:
        print("\n--- Обновление записи ---")
        try:
            student_id = self._read_int("ID записи для обновления: ")
            existing = self.database.select_record(student_id=student_id)
            if not existing:
                print(f"✗ Запись с ID={student_id} не найдена")
                return

            print("Текущие данные:", existing[0])
            print("(Оставьте поле пустым, чтобы не менять)")

            first_name = self._read_string_optional("Новое имя: ")
            second_name = self._read_string_optional("Новая фамилия: ")
            age = self._read_optional_int("Новый возраст: ")
            sex = self._read_string_optional("Новый пол (M/F): ")

            updated = self.database.update_record(student_id, first_name, second_name, age, sex)

            if updated:
                print(f"✓ Запись обновлена: {updated}")
            else:
                print("✗ Не удалось обновить запись")
        except InvalidAgeError as e:
            print(f"✗ Ошибка: {e}")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")

    def _delete_student(self) -> None:
        print("\n--- Удаление записи ---")
        try:
            student_id = self._read_int("ID записи для удаления: ")
            existing = self.database.select_record(student_id=student_id)
            if not existing:
                print(f"✗ Запись с ID={student_id} не найдена")
                return

            print("Запись для удаления:", existing[0])
            confirm = self._get_user_input("Вы уверены? (д/н): ").lower()

            if confirm in ('д', 'yes', 'y', 'да'):
                deleted = self.database.delete_record(student_id)
                if deleted:
                    print(f"✓ Запись с ID={student_id} удалена")
                else:
                    print("✗ Не удалось удалить запись")
            else:
                print("Удаление отменено")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")

    def _sort_students(self) -> None:
        print("\n--- Сортировка записей ---")
        print("Доступные поля для сортировки:")
        print("1. ID\n2. Имя (first_name)\n3. Фамилия (second_name)\n4. Возраст (age)\n5. Пол (sex)")

        field_choice = self._get_user_input("Выберите поле (1-5): ")
        field_map = {'1': 'id', '2': 'first_name', '3': 'second_name', '4': 'age', '5': 'sex'}

        if field_choice not in field_map:
            print("✗ Неверный выбор поля")
            return

        order = self._get_user_input("Порядок (1 - по возрастанию, 2 - по убыванию): ")
        reverse = (order == '2')

        try:
            sorted_records = self.database.sort_records(key=field_map[field_choice], reverse=reverse)
            if not sorted_records:
                print("Нет записей для сортировки")
                return
            print(f"\n✓ Отсортировано по полю '{field_map[field_choice]}' "
                  f"({'по возрастанию' if not reverse else 'по убыванию'}):")
            self._print_records(sorted_records)
        except InvalidSortFieldError as e:
            print(f"✗ Ошибка: {e}")

    def _manage_indexes(self) -> None:
        """Управление индексами для JSON БД."""
        if not hasattr(self.database, 'create_index'):
            print("✗ Индексация не поддерживается для данного типа БД")
            return

        print("\n--- Управление индексами ---")
        print("1. Показать существующие индексы")
        print("2. Создать индекс")
        print("3. Вернуться")

        choice = self._get_user_input("Выберите действие: ")

        if choice == '1':
            indices = self.database.get_indices()
            if indices:
                print(f"\n📊 Существующие индексы:")
                for field, count in indices.items():
                    print(f"  • {field}: {count} уникальных значений")
            else:
                print("\n📊 Индексы не созданы")
        elif choice == '2':
            print("\nДоступные поля для индексации:")
            print("1. ID\n2. Имя\n3. Фамилия\n4. Возраст\n5. Пол")
            field_choice = self._get_user_input("Выберите поле (1-5): ")
            field_map = {'1': 'id', '2': 'first_name', '3': 'second_name', '4': 'age', '5': 'sex'}
            if field_choice in field_map:
                try:
                    self.database.create_index(field_map[field_choice])
                    print(f"✓ Индекс для поля '{field_map[field_choice]}' создан")
                except InvalidSortFieldError as e:
                    print(f"✗ Ошибка: {e}")

    def _handle_action(self, action: str) -> None:
        actions = {
            "1": self._add_student,
            "2": self._show_all_students,
            "3": self._find_students_by_filter,
            "4": self._update_student,
            "5": self._delete_student,
            "6": self._sort_students,
            "0": self._exit_program,
        }

        if self.db_type == "json" and hasattr(self.database, 'create_index'):
            actions["7"] = self._manage_indexes

        handler = actions.get(action)
        if handler:
            try:
                handler()
            except (InvalidAgeError, DuplicateIDError, InvalidSortFieldError) as e:
                print(f"✗ Ошибка БД: {e}")
            except (DatabaseLoadError, DatabaseSaveError) as e:
                print(f"✗ Ошибка файла: {e}")
            except ValueError as e:
                print(f"✗ Ошибка ввода: {e}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
        else:
            print("Неизвестная команда.")

    def _exit_program(self) -> None:
        print("Выход из программы.")
        self.running = False


def run(db_type: str = "memory", db_path: str = "data/database") -> None:
    """Запускает TUI."""
    tui = StudentTUI(db_type, db_path)
    tui.run()


if __name__ == "__main__":
    run()