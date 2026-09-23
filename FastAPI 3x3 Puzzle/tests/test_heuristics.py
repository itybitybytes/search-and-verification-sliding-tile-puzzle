"""Tests for assignment-required heuristic functions."""

from __future__ import annotations

import unittest

from solver import LEFT, PuzzleState, manhattan_distance, misplaced_tiles


class HeuristicTests(unittest.TestCase):
    def test_heuristics_return_zero_for_primary_3x3_goal(self) -> None:
        goal = PuzzleState.goal(3)

        self.assertEqual(misplaced_tiles(goal), 0)
        self.assertEqual(manhattan_distance(goal), 0)

    def test_heuristics_return_zero_for_generalized_goals(self) -> None:
        for size in (4, 5):
            with self.subTest(size=size):
                goal = PuzzleState.goal(size)

                self.assertEqual(misplaced_tiles(goal), 0)
                self.assertEqual(manhattan_distance(goal), 0)

    def test_blank_does_not_contribute_to_misplaced_or_manhattan(self) -> None:
        state = PuzzleState((1, 2, 3, 4, 5, 6, 0, 7, 8), 3)

        self.assertEqual(misplaced_tiles(state), 2)
        self.assertEqual(manhattan_distance(state), 2)

    def test_known_non_goal_3x3_values(self) -> None:
        state = PuzzleState((1, 2, 3, 0, 4, 6, 7, 5, 8), 3)

        self.assertEqual(misplaced_tiles(state), 3)
        self.assertEqual(manhattan_distance(state), 3)

    def test_heuristics_accept_raw_tuple_input_with_size(self) -> None:
        board = (1, 2, 3, 4, 5, 6, 7, 0, 8)

        self.assertEqual(misplaced_tiles(board, 3), 1)
        self.assertEqual(manhattan_distance(board, 3), 1)

    def test_generalized_4x4_known_one_move_values(self) -> None:
        state = PuzzleState.goal(4).apply_move(LEFT)

        self.assertEqual(misplaced_tiles(state), 1)
        self.assertEqual(manhattan_distance(state), 1)

    def test_generalized_5x5_known_one_move_values(self) -> None:
        state = PuzzleState.goal(5).apply_move(LEFT)

        self.assertEqual(misplaced_tiles(state), 1)
        self.assertEqual(manhattan_distance(state), 1)


if __name__ == "__main__":
    unittest.main()
