import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.student_table = StudentTable()
        self.student_table.clear()

    def test_student_table_allocation(self):
        self.assertIsInstance(self.student_table, StudentTable)

    def test_create_record(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.student_table.create_record(*test_data)
                self.assertEqual(record, test_data)

    def test_create_record_negative_age(self):
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
        ]
        error_message = "Поле age не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidAgeError) as context:
                    self.student_table.create_record(*test_data)
                self.assertEqual(str(context.exception), error_message)

    def test_create_record_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.student_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

    def test_create_record_with_whitespace(self):
        self.student_table.clear()
        record = self.student_table.create_record(1, "  John  ", "  Doe  ", 20, "  M  ")
        self.assertEqual(record[1], "John")
        self.assertEqual(record[2], "Doe")
        self.assertEqual(record[4], "M")

    def test_create_record_extreme_values(self):
        self.student_table.clear()
        record1 = self.student_table.create_record(999999, "John", "Doe", 20, "M")
        self.assertEqual(record1[0], 999999)

        record2 = self.student_table.create_record(2, "Jane", "Smith", 150, "F")
        self.assertEqual(record2[3], 150)

        long_name = "A" * 100
        record3 = self.student_table.create_record(3, long_name, long_name, 20, "M")
        self.assertEqual(record3[1], long_name)
        self.assertEqual(record3[2], long_name)

    def test_select_record_no_filters(self):
        self.student_table.clear()
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        records = self.student_table.select_record()
        self.assertEqual(len(records), 2)

    def test_select_record_with_filters(self):
        self.student_table.clear()
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "John", "Smith", 20, "M"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        cases = [
            ({"student_id": 1}, 1),
            ({"first_name": "John"}, 2),
            ({"second_name": "Smith"}, 2),
            ({"age": 20}, 2),
            ({"sex": "M"}, 2),
            ({"first_name": "John", "age": 20}, 2),
            ({"first_name": "Jane", "second_name": "Smith"}, 1),
        ]

        for filters, expected_count in cases:
            with self.subTest(filters=filters):
                records = self.student_table.select_record(**filters)
                self.assertEqual(len(records), expected_count)

    def test_select_record_all_filters_none(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        records = self.student_table.select_record(
            student_id=None, first_name=None, second_name=None, age=None, sex=None
        )
        self.assertEqual(len(records), 1)

    def test_select_record_empty_string_filters(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        records = self.student_table.select_record(
            student_id=None, first_name="", second_name=None, age=None, sex=""
        )
        self.assertEqual(len(records), 1)

    def test_update_record_all_fields(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        updated = self.student_table.update_record(1, "Jonathan", "Smith", 25, "M")
        expected = (1, "Jonathan", "Smith", 25, "M")
        self.assertEqual(updated, expected)

    def test_update_record_partial_fields(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        updated = self.student_table.update_record(1, first_name="Johnny")
        expected = (1, "Johnny", "Doe", 20, "M")
        self.assertEqual(updated, expected)

        updated = self.student_table.update_record(1, age=22)
        expected = (1, "Johnny", "Doe", 22, "M")
        self.assertEqual(updated, expected)

    def test_update_record_all_none(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        updated = self.student_table.update_record(1, None, None, None, None)
        expected = (1, "John", "Doe", 20, "M")
        self.assertEqual(updated, expected)

    def test_update_record_empty_strings(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        updated = self.student_table.update_record(1, "", "", None, "")
        expected = (1, "", "", 20, "")
        self.assertEqual(updated, expected)

    def test_update_record_negative_age(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        with self.assertRaises(InvalidAgeError) as context:
            self.student_table.update_record(1, age=-5)
        self.assertEqual(str(context.exception), "Поле age не может быть отрицательным.")

    def test_update_record_not_found(self):
        self.student_table.clear()
        result = self.student_table.update_record(999, first_name="Test")
        self.assertIsNone(result)

    def test_delete_record_from_beginning(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")

        result = self.student_table.delete_record(1)
        self.assertTrue(result)

        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 2)

    def test_delete_record_from_middle(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")

        result = self.student_table.delete_record(2)
        self.assertTrue(result)

        records = self.student_table.select_record()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0][0], 1)
        self.assertEqual(records[1][0], 3)

    def test_delete_record_from_end(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")

        result = self.student_table.delete_record(2)
        self.assertTrue(result)

        records = self.student_table.select_record()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 1)

    def test_delete_record_not_found(self):
        self.student_table.clear()
        result = self.student_table.delete_record(999)
        self.assertFalse(result)

    def test_clear_empty_table(self):
        self.student_table.clear()
        self.assertEqual(len(self.student_table.select_record()), 0)

        self.student_table.clear()
        self.assertEqual(len(self.student_table.select_record()), 0)

    def test_clear_non_empty_table(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")

        self.assertEqual(len(self.student_table.select_record()), 2)

        self.student_table.clear()
        self.assertEqual(len(self.student_table.select_record()), 0)

    def test_get_all_records_empty(self):
        self.student_table.clear()
        records = self.student_table.get_all_records()
        self.assertEqual(len(records), 0)
        self.assertEqual(records, [])

    def test_get_all_records_non_empty(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")

        records = self.student_table.get_all_records()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0][1], "John")
        self.assertEqual(records[1][1], "Jane")

    def test_get_all_records_returns_copy(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        records_copy = self.student_table.get_all_records()
        if records_copy:
            records_copy[0] = (999, "Changed", "Changed", 99, "X")

        original = self.student_table.select_record()
        self.assertEqual(original[0][0], 1)
        self.assertEqual(original[0][1], "John")

    def test_sort_records_by_id(self):
        self.student_table.clear()
        self.student_table.create_record(3, "Charlie", "Brown", 22, "M")
        self.student_table.create_record(1, "Alice", "Smith", 20, "F")
        self.student_table.create_record(2, "Bob", "Johnson", 21, "M")

        all_records = self.student_table.select_record()

        sorted_by_id = sorted(all_records, key=lambda r: r[0])
        self.assertEqual([r[0] for r in sorted_by_id], [1, 2, 3])

        sorted_by_id_desc = sorted(all_records, key=lambda r: r[0], reverse=True)
        self.assertEqual([r[0] for r in sorted_by_id_desc], [3, 2, 1])

    def test_sort_records_by_name(self):
        self.student_table.clear()
        self.student_table.create_record(1, "Charlie", "Brown", 22, "M")
        self.student_table.create_record(2, "Alice", "Smith", 20, "F")
        self.student_table.create_record(3, "Bob", "Johnson", 21, "M")

        all_records = self.student_table.select_record()

        sorted_by_first = sorted(all_records, key=lambda r: r[1])
        self.assertEqual([r[1] for r in sorted_by_first], ["Alice", "Bob", "Charlie"])

        sorted_by_last = sorted(all_records, key=lambda r: r[2])
        self.assertEqual([r[2] for r in sorted_by_last], ["Brown", "Johnson", "Smith"])

    def test_sort_records_by_age(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 22, "M")
        self.student_table.create_record(2, "Jane", "Smith", 20, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")

        all_records = self.student_table.select_record()

        sorted_by_age = sorted(all_records, key=lambda r: r[3])
        self.assertEqual([r[3] for r in sorted_by_age], [20, 21, 22])

        sorted_by_age_desc = sorted(all_records, key=lambda r: r[3], reverse=True)
        self.assertEqual([r[3] for r in sorted_by_age_desc], [22, 21, 20])

    def test_sort_records_by_sex(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")

        all_records = self.student_table.select_record()

        sorted_by_sex = sorted(all_records, key=lambda r: r[4])
        self.assertEqual([r[4] for r in sorted_by_sex], ["F", "M", "M"])

    def test_sort_records_with_duplicates(self):
        self.student_table.clear()
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 20, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")

        all_records = self.student_table.select_record()
        sorted_by_age = sorted(all_records, key=lambda r: r[3])
        self.assertEqual(sorted_by_age[0][3], 20)
        self.assertEqual(sorted_by_age[1][3], 20)
        self.assertEqual(sorted_by_age[2][3], 21)


if __name__ == '__main__':
    unittest.main()