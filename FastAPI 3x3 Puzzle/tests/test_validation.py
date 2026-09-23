"""Focused tests for invalid-state and solvability handling."""

import unittest

from solver import (
    InvalidPuzzleStateError,
    PuzzleState,
    create_goal_state,
    is_solvable,
    validate_board,
)


class ValidationTests(unittest.TestCase):
    def test_valid_3x3(self):
        validated = validate_board(create_goal_state(3), 3)
        self.assertEqual(validated.size, 3)
        self.assertEqual(validated.tiles, create_goal_state(3))

    def test_valid_4x4(self):
        validated = validate_board(create_goal_state(4), 4)
        self.assertEqual(validated.size, 4)
        self.assertEqual(validated.tiles, create_goal_state(4))

    def test_valid_5x5(self):
        validated = validate_board(create_goal_state(5), 5)
        self.assertEqual(validated.size, 5)
        self.assertEqual(validated.tiles, create_goal_state(5))

    def test_duplicate_tile_is_invalid(self):
        with self.assertRaises(InvalidPuzzleStateError):
            validate_board((1, 2, 3, 4, 5, 6, 7, 7, 0), 3)

    def test_missing_tile_is_invalid(self):
        with self.assertRaises(InvalidPuzzleStateError):
            validate_board((1, 2, 3, 4, 5, 6, 7, 0, 0), 3)

    def test_wrong_out_of_range_tile_is_invalid(self):
        with self.assertRaises(InvalidPuzzleStateError):
            validate_board((1, 2, 3, 4, 5, 6, 7, 8, 9), 3)

    def test_wrong_board_length_is_invalid(self):
        with self.assertRaises(InvalidPuzzleStateError):
            validate_board((1, 2, 3, 4, 5, 6, 7, 0), 3)

    def test_puzzle_state_rejects_malformed_board(self):
        with self.assertRaises(InvalidPuzzleStateError):
            PuzzleState((1, 2, 3, 4, 5, 6, 7, 8, 8), 3)


class SolvabilityTests(unittest.TestCase):
    def test_known_solvable_3x3(self):
        self.assertTrue(is_solvable((1, 2, 3, 4, 5, 6, 7, 0, 8), 3))

    def test_known_unsolvable_3x3(self):
        self.assertFalse(is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0), 3))

    def test_solvable_4x4_parity_case(self):
        self.assertTrue(is_solvable(create_goal_state(4), 4))

    def test_unsolvable_4x4_parity_case(self):
        self.assertFalse(
            is_solvable(
                (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0),
                4,
            )
        )

    def test_solvable_5x5_sanity_case(self):
        self.assertTrue(is_solvable(create_goal_state(5), 5))


if __name__ == "__main__":
    unittest.main()
