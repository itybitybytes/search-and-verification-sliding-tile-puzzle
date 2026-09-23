"""Focused tests for the generalized sliding-tile puzzle model."""

import unittest

from solver import DOWN, LEFT, RIGHT, UP, PuzzleState, create_goal_state


class PuzzleStateTests(unittest.TestCase):
    def test_3x3_goal(self):
        self.assertEqual(create_goal_state(3), (1, 2, 3, 4, 5, 6, 7, 8, 0))
        self.assertTrue(PuzzleState.goal(3).is_goal())

    def test_4x4_goal(self):
        self.assertEqual(
            create_goal_state(4),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0),
        )
        self.assertTrue(PuzzleState.goal(4).is_goal())

    def test_5x5_goal(self):
        self.assertEqual(create_goal_state(5), tuple(range(1, 25)) + (0,))
        self.assertTrue(PuzzleState.goal(5).is_goal())

    def test_legal_moves_from_corners(self):
        lower_right_blank = PuzzleState.goal(3)
        self.assertEqual(lower_right_blank.legal_moves(), (UP, LEFT))

        upper_left_blank = PuzzleState((0, 1, 2, 3, 4, 5, 6, 7, 8), 3)
        self.assertEqual(upper_left_blank.legal_moves(), (DOWN, RIGHT))

    def test_legal_moves_from_edges(self):
        top_edge_blank = PuzzleState((1, 0, 2, 3, 4, 5, 6, 7, 8), 3)
        self.assertEqual(top_edge_blank.legal_moves(), (DOWN, LEFT, RIGHT))

        left_edge_blank = PuzzleState((1, 2, 3, 0, 4, 5, 6, 7, 8), 3)
        self.assertEqual(left_edge_blank.legal_moves(), (UP, DOWN, RIGHT))

    def test_legal_moves_from_interior_position(self):
        center_blank = PuzzleState((1, 2, 3, 4, 0, 5, 6, 7, 8), 3)
        self.assertEqual(center_blank.legal_moves(), (UP, DOWN, LEFT, RIGHT))

    def test_move_application_uses_blank_movement_semantics(self):
        state = PuzzleState.goal(3)
        moved = state.apply_move(UP)
        self.assertEqual(moved.tiles, (1, 2, 3, 4, 5, 0, 7, 8, 6))
        self.assertEqual(moved.blank_position(), (1, 2))

    def test_successor_generation_returns_moves_and_states(self):
        state = PuzzleState.goal(3)
        successors = state.successors()
        self.assertEqual([move for move, _ in successors], [UP, LEFT])
        self.assertEqual([next_state.tiles for _, next_state in successors], [
            (1, 2, 3, 4, 5, 0, 7, 8, 6),
            (1, 2, 3, 4, 5, 6, 7, 0, 8),
        ])

    def test_goal_recognition(self):
        self.assertTrue(PuzzleState.goal(3).is_goal())
        self.assertFalse(PuzzleState.goal(3).apply_move(LEFT).is_goal())

    def test_states_are_hashable_and_comparable(self):
        state_a = PuzzleState.goal(4)
        state_b = PuzzleState(create_goal_state(4), 4)
        self.assertEqual(state_a, state_b)
        self.assertEqual(len({state_a, state_b}), 1)

    def test_format_board_for_reviewer_inspection(self):
        self.assertEqual(PuzzleState.goal(3).format(), "1 2 3\n4 5 6\n7 8 _")


if __name__ == "__main__":
    unittest.main()
