from __future__ import annotations

import unittest

from puzzle.validation import (
    InvalidPuzzleStateError,
    blank_row_from_bottom,
    count_inversions,
    infer_dimension,
    is_solvable,
    validate_board,
)


class ValidationTests(unittest.TestCase):
    def test_valid_boards_for_supported_sizes(self) -> None:
        for size in (3, 4, 5):
            board = tuple(range(1, size * size)) + (0,)
            with self.subTest(size=size):
                self.assertEqual(validate_board(board), (board, size))
                self.assertEqual(infer_dimension(board), size)

    def test_rejects_duplicate_tile(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "duplicate"):
            validate_board((1, 2, 3, 4, 5, 6, 7, 7, 0))

    def test_rejects_missing_tile(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "missing"):
            validate_board((1, 2, 3, 4, 5, 6, 7, 9, 0))

    def test_rejects_out_of_range_tile(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "out-of-range"):
            validate_board((1, 2, 3, 4, 5, 6, 7, 99, 0))

    def test_rejects_wrong_length(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "square"):
            validate_board((1, 2, 3, 4, 5, 6, 7, 0))

    def test_rejects_multiple_blanks(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "exactly one blank"):
            validate_board((1, 2, 3, 4, 5, 6, 0, 8, 0))

    def test_rejects_missing_blank(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "exactly one blank"):
            validate_board((1, 2, 3, 4, 5, 6, 7, 8, 9))

    def test_rejects_size_length_mismatch(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "does not match"):
            validate_board((1, 2, 3, 4, 5, 6, 7, 8, 0), size=4)

    def test_rejects_non_integer_tiles(self) -> None:
        with self.assertRaisesRegex(InvalidPuzzleStateError, "integers"):
            validate_board((1, 2, 3, 4, 5, 6, 7, "8", 0))

    def test_known_3x3_solvable_and_unsolvable(self) -> None:
        self.assertTrue(is_solvable((1, 2, 3, 4, 5, 6, 7, 0, 8)))
        self.assertFalse(is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0)))

    def test_known_4x4_solvable_and_unsolvable_parity(self) -> None:
        goal_4 = tuple(range(1, 16)) + (0,)
        one_move_4 = tuple(range(1, 15)) + (0, 15)
        unsolvable_4 = tuple(range(1, 14)) + (15, 14, 0)
        self.assertTrue(is_solvable(goal_4))
        self.assertTrue(is_solvable(one_move_4))
        self.assertFalse(is_solvable(unsolvable_4))

    def test_5x5_solvability_sanity(self) -> None:
        goal_5 = tuple(range(1, 25)) + (0,)
        unsolvable_5 = tuple(range(1, 23)) + (24, 23, 0)
        self.assertTrue(is_solvable(goal_5))
        self.assertFalse(is_solvable(unsolvable_5))

    def test_inversion_and_blank_row_helpers(self) -> None:
        board = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        self.assertEqual(count_inversions(board), 1)
        self.assertEqual(blank_row_from_bottom(board), 1)


if __name__ == "__main__":
    unittest.main()
