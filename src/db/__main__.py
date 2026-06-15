"""Точка входа для запуска из командной строки."""

import argparse
import sys
from src.db.tui import run


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Система управления БД студентов")
    parser.add_argument(
        '--db-type', '-t',
        choices=['memory', 'json', 'csv'],
        default='memory',
        help='Тип БД (по умолчанию: memory)'
    )
    parser.add_argument(
        '--db-path', '-p',
        default='data/database',
        help='Путь к файлу БД (по умолчанию: data/database)'
    )

    args = parser.parse_args()

    print(f"Запуск с БД типа: {args.db_type}")
    print(f"Путь: {args.db_path}")
    print("=" * 50)

    try:
        run(db_type=args.db_type, db_path=args.db_path)
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()