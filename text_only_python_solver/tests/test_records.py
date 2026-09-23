from __future__ import annotations

import unittest
from pathlib import Path

from puzzle import (
    append_record,
    format_elapsed_time,
    load_records,
    records_for_username,
    save_records,
    validate_completion_record,
)

TEST_DIR = Path(__file__).resolve().parent


def remove_if_present(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


class CompletionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_paths = [
            TEST_DIR / "_tmp_missing_records.json",
            TEST_DIR / "_tmp_empty_records.json",
            TEST_DIR / "_tmp_bad_records.json",
            TEST_DIR / "_tmp_completion_records.json",
        ]
        for path in self.temp_paths:
            remove_if_present(path)

    def tearDown(self) -> None:
        for path in self.temp_paths:
            remove_if_present(path)

    def test_load_records_handles_missing_empty_and_malformed_files(self) -> None:
        missing = TEST_DIR / "_tmp_missing_records.json"
        self.assertEqual(load_records(missing), [])

        empty = TEST_DIR / "_tmp_empty_records.json"
        empty.write_text("", encoding="utf-8")
        self.assertEqual(load_records(empty), [])

        malformed = TEST_DIR / "_tmp_bad_records.json"
        malformed.write_text("{not json", encoding="utf-8")
        self.assertEqual(load_records(malformed), [])

    def test_append_load_and_filter_records_by_username(self) -> None:
        path = TEST_DIR / "_tmp_completion_records.json"
        first = append_record("alex", "Easy", 3, 12, 75, path)
        second = append_record("sam", "Medium", 4, 30, 125, path)
        third = append_record("alex", "Hard", 5, 44, 3661, path)

        records = load_records(path)
        self.assertEqual(records, [first, second, third])
        self.assertEqual(records_for_username("alex", path), [first, third])
        self.assertEqual(records_for_username("nobody", path), [])
        self.assertEqual(first["formatted_time"], "1:15")
        self.assertEqual(third["formatted_time"], "1:01:01")

    def test_save_records_validates_before_writing(self) -> None:
        path = TEST_DIR / "_tmp_completion_records.json"
        record = validate_completion_record(
            {
                "username": "taylor",
                "difficulty": "Easy",
                "board_size": 3,
                "moves": 10,
                "elapsed_seconds": 61,
                "completed_at": "2026-09-02T00:00:00+00:00",
            }
        )
        save_records([record], path)
        self.assertEqual(load_records(path), [record])

    def test_validation_rejects_bad_completion_data(self) -> None:
        base = {
            "username": "taylor",
            "difficulty": "Easy",
            "board_size": 3,
            "moves": 10,
            "elapsed_seconds": 61,
            "completed_at": "2026-09-02T00:00:00+00:00",
        }
        bad_cases = (
            {**base, "username": " "},
            {**base, "username": "x" * 41},
            {**base, "board_size": 6},
            {**base, "difficulty": "Hard"},
            {**base, "moves": -1},
            {**base, "elapsed_seconds": -1},
            {**base, "completed_at": ""},
        )

        for record in bad_cases:
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    validate_completion_record(record)

    def test_format_elapsed_time_rejects_invalid_values(self) -> None:
        self.assertEqual(format_elapsed_time(0), "0:00")
        with self.assertRaises(ValueError):
            format_elapsed_time(-1)


if __name__ == "__main__":
    unittest.main()
