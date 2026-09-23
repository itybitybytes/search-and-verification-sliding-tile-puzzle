"""Tests for fixed 3x3 verification case constants."""

from __future__ import annotations

import unittest

from solver import (
    COMPARISON_BFS_MINIMUM_LENGTH,
    COMPARISON_BOARD,
    COMPARISON_SEQUENCE_FROM_GOAL,
    INVALID_BOARD,
    ONE_MOVE_BFS_MINIMUM_LENGTH,
    ONE_MOVE_BOARD,
    ONE_MOVE_SEQUENCE_FROM_GOAL,
    SEVERAL_MOVE_BFS_MINIMUM_LENGTH,
    SEVERAL_MOVE_BOARD,
    SEVERAL_MOVE_SEQUENCE_FROM_GOAL,
    SOLVED_BOARD,
    UNSOLVABLE_BOARD,
    VERIFICATION_CASES,
    VERIFICATION_SIZE,
    InvalidPuzzleStateError,
    PuzzleState,
    breadth_first_search,
    is_solvable,
    validate_board,
)


def board_after_sequence(sequence: tuple[str, ...]) -> tuple[int, ...]:
    state = PuzzleState.goal(VERIFICATION_SIZE)
    for move in sequence:
        state = state.apply_move(move)
    return state.tiles


class VerificationCaseTests(unittest.TestCase):
    def test_solved_board_is_primary_3x3_goal(self) -> None:
        self.assertEqual(SOLVED_BOARD, PuzzleState.goal(3).tiles)

    def test_one_move_board_is_legal_scramble_with_bfs_minimum_length(self) -> None:
        self.assertEqual(ONE_MOVE_BOARD, board_after_sequence(ONE_MOVE_SEQUENCE_FROM_GOAL))
        result = breadth_first_search(ONE_MOVE_BOARD, VERIFICATION_SIZE)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, ONE_MOVE_BFS_MINIMUM_LENGTH)

    def test_several_move_board_is_legal_scramble_with_bfs_minimum_length(self) -> None:
        self.assertEqual(SEVERAL_MOVE_BOARD, board_after_sequence(SEVERAL_MOVE_SEQUENCE_FROM_GOAL))
        result = breadth_first_search(SEVERAL_MOVE_BOARD, VERIFICATION_SIZE)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, SEVERAL_MOVE_BFS_MINIMUM_LENGTH)

    def test_invalid_board_is_malformed_duplicate_and_missing_tile(self) -> None:
        with self.assertRaises(InvalidPuzzleStateError):
            validate_board(INVALID_BOARD, VERIFICATION_SIZE)

    def test_unsolvable_board_is_valid_but_wrong_parity(self) -> None:
        validate_board(UNSOLVABLE_BOARD, VERIFICATION_SIZE)
        self.assertFalse(is_solvable(UNSOLVABLE_BOARD, VERIFICATION_SIZE))

    def test_comparison_board_is_legal_scramble_with_bfs_minimum_length(self) -> None:
        self.assertEqual(COMPARISON_BOARD, board_after_sequence(COMPARISON_SEQUENCE_FROM_GOAL))
        result = breadth_first_search(COMPARISON_BOARD, VERIFICATION_SIZE)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, COMPARISON_BFS_MINIMUM_LENGTH)

    def test_named_verification_case_collection_contains_all_required_boards(self) -> None:
        self.assertEqual(
            set(VERIFICATION_CASES),
            {"solved", "one_move", "several_moves", "invalid", "unsolvable", "comparison"},
        )


if __name__ == "__main__":
    unittest.main()
