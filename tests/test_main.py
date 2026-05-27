"""Тесты для точки входа __main__.py."""

import pytest
from unittest.mock import patch
import argparse


class TestMain:
    """Тесты для main функции."""

    @patch('argparse.ArgumentParser.parse_args')
    @patch('src.db.__main__.run')
    def test_main_memory(self, mock_run, mock_args):
        """Тест запуска с memory БД."""
        mock_args.return_value = argparse.Namespace(
            db_type='memory',
            db_path='data/database'
        )
        from src.db import __main__
        __main__.main()
        mock_run.assert_called_once_with(
            db_type='memory',
            db_path='data/database'
        )

    @patch('argparse.ArgumentParser.parse_args')
    @patch('src.db.__main__.run')
    def test_main_json(self, mock_run, mock_args):
        """Тест запуска с JSON БД."""
        mock_args.return_value = argparse.Namespace(
            db_type='json',
            db_path='data/my_db'
        )
        from src.db import __main__
        __main__.main()
        mock_run.assert_called_once_with(
            db_type='json',
            db_path='data/my_db'
        )

    @patch('argparse.ArgumentParser.parse_args')
    @patch('src.db.__main__.run')
    def test_main_csv(self, mock_run, mock_args):
        """Тест запуска с CSV БД."""
        mock_args.return_value = argparse.Namespace(
            db_type='csv',
            db_path='custom/path'
        )
        from src.db import __main__
        __main__.main()
        mock_run.assert_called_once_with(
            db_type='csv',
            db_path='custom/path'
        )

    @patch('argparse.ArgumentParser.parse_args')
    @patch('src.db.__main__.run')
    def test_main_keyboard_interrupt(self, mock_run, mock_args):
        """Тест обработки Ctrl+C."""
        mock_args.return_value = argparse.Namespace(
            db_type='memory',
            db_path='data/database'
        )
        mock_run.side_effect = KeyboardInterrupt()
        from src.db import __main__
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                __main__.main()
            assert exc_info.value.code == 0
            mock_print.assert_any_call("\nПрограмма завершена")

    @patch('argparse.ArgumentParser.parse_args')
    @patch('src.db.__main__.run')
    def test_main_exception(self, mock_run, mock_args):
        """Тест обработки исключения."""
        mock_args.return_value = argparse.Namespace(
            db_type='memory',
            db_path='data/database'
        )
        mock_run.side_effect = Exception("Тестовая ошибка")
        from src.db import __main__
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                __main__.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call("Критическая ошибка: Тестовая ошибка")