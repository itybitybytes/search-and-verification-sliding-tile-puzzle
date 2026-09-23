from __future__ import annotations

import unittest

from puzzle import goal_board, manhattan_distance, misplaced_tiles


class HeuristicTests(unittest.TestCase):
    def test_heuristics_are_zero_at_3x3_goal(self) -> None:
        goal = goal_board(3)
        self.assertEqual(misplaced_tiles(goal), 0)
        self.assertEqual(manhattan_distance(goal), 0)

    def test_heuristics_are_zero_at_generalized_goals(self) -> None:
        for size in (4, 5):
            with self.subTest(size=size):
                goal = goal_board(size)
                self.assertEqual(misplaced_tiles(goal), 0)
                self.assertEqual(manhattan_distance(goal), 0)

    def test_blank_does_not_contribute_to_heuristics(self) -> None:
        board = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.assertEqual(misplaced_tiles(board), 1)
        self.assertEqual(manhattan_distance(board), 1)

    def test_known_non_goal_heuristic_values(self) -> None:
        board = (1, 2, 3, 7, 0, 6, 5, 4, 8)
        self.assertEqual(misplaced_tiles(board), 4)
        self.assertEqual(manhattan_distance(board), 6)

    def test_heuristics_are_dimension_aware(self) -> None:
        board_4 = tuple(range(1, 15)) + (0, 15)
        self.assertEqual(misplaced_tiles(board_4), 1)
        self.assertEqual(manhattan_distance(board_4), 1)


if __name__ == "__main__":
    unittest.main()
