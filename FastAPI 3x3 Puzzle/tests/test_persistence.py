"""Tests for server-side completion persistence."""

from __future__ import annotations

from pathlib import Path
import unittest

from web.persistence import (
    CompletionValidationError,
    create_completion_record,
    list_completion_records,
)

TEST_DATA_DIR = Path("test_data")


class CompletionPersistenceTests(unittest.TestCase):
    def test_multiple_users_records_sizes_and_reconnect_reads(self) -> None:
        TEST_DATA_DIR.mkdir(exist_ok=True)
        db_path = TEST_DATA_DIR / "persistence-valid.sqlite3"
        db_path.unlink(missing_ok=True)

        first = create_completion_record("Ada", 3, 42, 15, db_path)
        second = create_completion_record("Grace", 4, 88, 31, db_path)
        third = create_completion_record("Ada", 5, 120, 44, db_path)

        records = list_completion_records(db_path)

        self.assertEqual([record.id for record in records], [first.id, second.id, third.id])
        self.assertEqual([record.username for record in records], ["Ada", "Grace", "Ada"])
        self.assertEqual([record.board_size for record in records], [3, 4, 5])
        self.assertEqual([record.duration_seconds for record in records], [42, 88, 120])
        self.assertEqual([record.move_count for record in records], [15, 31, 44])
        self.assertTrue(all(record.completed_at.endswith("Z") for record in records))

        reopened_records = list_completion_records(db_path)
        self.assertEqual([record.as_dict() for record in reopened_records], [record.as_dict() for record in records])

    def test_validation_rejects_bad_completion_data(self) -> None:
        TEST_DATA_DIR.mkdir(exist_ok=True)
        db_path = TEST_DATA_DIR / "persistence-invalid.sqlite3"
        db_path.unlink(missing_ok=True)

        bad_inputs = (
            ("", 3, 10, 1),
            ("x" * 33, 3, 10, 1),
            ("Ada", 6, 10, 1),
            ("Ada", 3, -1, 1),
            ("Ada", 3, 10, -1),
        )

        for payload in bad_inputs:
            with self.subTest(payload=payload):
                with self.assertRaises(CompletionValidationError):
                    create_completion_record(*payload, db_path=db_path)

        self.assertEqual(list_completion_records(db_path), [])


if __name__ == "__main__":
    unittest.main()
