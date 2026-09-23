from __future__ import annotations

import unittest

from puzzle import PuzzleState, goal_board


class PuzzleModelTests(unittest.TestCase):
    def test_goal_boards_for_supported_sizes(self) -> None:
        self.assertEqual(goal_board(3), (1, 2, 3, 4, 5, 6, 7, 8, 0))
        self.assertEqual(
            goal_board(4),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0),
        )
        self.assertEqual(goal_board(5), tuple(range(1, 25)) + (0,))

    def test_goal_recognition(self) -> None:
        self.assertTrue(PuzzleState.goal(3).is_goal())
        self.assertFalse(PuzzleState((1, 2, 3, 4, 5, 6, 7, 0, 8)).is_goal())

    def test_dimension_and_coordinate_conversion(self) -> None:
        state = PuzzleState.goal(4)
        self.assertEqual(state.dimension, 4)
        self.assertEqual(state.index_to_coordinate(14), (3, 2))
        self.assertEqual(state.coordinate_to_index(3, 2), 14)

    def test_legal_moves_from_corner(self) -> None:
        state = PuzzleState.goal(3)
        self.assertEqual(state.blank_index(), 8)
        self.assertEqual(state.legal_moves(), ("UP", "LEFT"))

    def test_legal_moves_from_edge(self) -> None:
        state = PuzzleState((1, 0, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(state.index_to_coordinate(state.blank_index()), (0, 1))
        self.assertEqual(state.legal_moves(), ("DOWN", "LEFT", "RIGHT"))

    def test_legal_moves_from_interior(self) -> None:
        state = PuzzleState((1, 2, 3, 4, 0, 5, 6, 7, 8))
        self.assertEqual(state.index_to_coordinate(state.blank_index()), (1, 1))
        self.assertEqual(state.legal_moves(), ("UP", "DOWN", "LEFT", "RIGHT"))

    def test_apply_move_uses_blank_movement_semantics(self) -> None:
        state = PuzzleState.goal(3)
        moved = state.apply_move("LEFT")
        self.assertEqual(moved.board, (1, 2, 3, 4, 5, 6, 7, 0, 8))
        self.assertEqual(moved.apply_move("RIGHT"), state)

    def test_apply_move_rejects_off_board_and_unknown_moves(self) -> None:
        state = PuzzleState.goal(3)
        with self.assertRaises(ValueError):
            state.apply_move("DOWN")
        with self.assertRaises(ValueError):
            state.apply_move("DIAGONAL")

    def test_successors_pair_moves_with_new_states(self) -> None:
        state = PuzzleState.goal(3)
        successors = state.successors()
        self.assertEqual([move for move, _ in successors], ["UP", "LEFT"])
        self.assertEqual(
            [successor.board for _, successor in successors],
            [
                (1, 2, 3, 4, 5, 0, 7, 8, 6),
                (1, 2, 3, 4, 5, 6, 7, 0, 8),
            ],
        )

    def test_equality_and_hash_use_immutable_tuple_state(self) -> None:
        first = PuzzleState.goal(3)
        second = PuzzleState((1, 2, 3, 4, 5, 6, 7, 8, 0))
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertEqual({first, second}, {first})

    def test_terminal_rendering_supports_unicode_and_ascii_blank(self) -> None:
        state = PuzzleState.goal(5)
        unicode_render = state.render(use_unicode_blank=True)
        ascii_render = state.render(use_unicode_blank=False)
        self.assertIn("\U0001fa93", unicode_render)
        self.assertIn("__", ascii_render)
        self.assertEqual(len(set(len(line) for line in ascii_render.splitlines())), 1)


if __name__ == "__main__":
    unittest.main()
