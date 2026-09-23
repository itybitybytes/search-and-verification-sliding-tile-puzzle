"""Tests for breadth-first search behavior."""

from __future__ import annotations

import unittest

from solver import (
    LEFT,
    RIGHT,
    STATUS_INVALID,
    STATUS_SOLVED,
    STATUS_UNSOLVABLE,
    UP,
    PuzzleState,
    a_star_manhattan,
    a_star_misplaced,
    breadth_first_search,
)


def apply_moves(state: PuzzleState, moves: tuple[str, ...]) -> PuzzleState:
    current = state
    for move in moves:
        current = current.apply_move(move)
    return current


class BreadthFirstSearchTests(unittest.TestCase):
    def test_solved_state_returns_zero_length_solution(self) -> None:
        start = PuzzleState.goal(3)

        result = breadth_first_search(start)

        self.assertTrue(result.solved)
        self.assertEqual(result.status, STATUS_SOLVED)
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertEqual(result.expanded_states, 0)
        self.assertEqual(result.state_path, (start,))

    def test_one_move_state_returns_single_minimum_move(self) -> None:
        goal = PuzzleState.goal(3)
        start = goal.apply_move(LEFT)

        result = breadth_first_search(start)

        self.assertTrue(result.solved)
        self.assertEqual(result.moves, (RIGHT,))
        self.assertEqual(result.solution_length, 1)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertGreater(result.expanded_states, 0)
        self.assertEqual(apply_moves(start, result.moves), goal)

    def test_several_move_state_returns_expected_minimum_length(self) -> None:
        goal = PuzzleState.goal(3)
        start = goal.apply_move(LEFT).apply_move(UP).apply_move(LEFT)

        result = breadth_first_search(start)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, 3)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertEqual(apply_moves(start, result.moves), goal)
        self.assertGreater(result.expanded_states, 0)

    def test_bfs_accepts_raw_tuple_board_input(self) -> None:
        start = (1, 2, 3, 4, 5, 6, 7, 0, 8)

        result = breadth_first_search(start)

        self.assertTrue(result.solved)
        self.assertEqual(result.moves, (RIGHT,))
        self.assertEqual(result.solution_length, 1)

    def test_invalid_state_returns_invalid_result_without_search(self) -> None:
        result = breadth_first_search((1, 2, 3, 4, 5, 6, 7, 7, 0))

        self.assertFalse(result.solved)
        self.assertEqual(result.status, STATUS_INVALID)
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.expanded_states, 0)

    def test_unsolvable_state_returns_unsolvable_result_without_exhaustive_search(self) -> None:
        result = breadth_first_search((1, 2, 3, 4, 5, 6, 8, 7, 0))

        self.assertFalse(result.solved)
        self.assertEqual(result.status, STATUS_UNSOLVABLE)
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.expanded_states, 0)

    def test_returned_state_path_matches_move_sequence(self) -> None:
        goal = PuzzleState.goal(3)
        start = goal.apply_move(LEFT).apply_move(UP)

        result = breadth_first_search(start)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertEqual(result.state_path[0], start)
        self.assertEqual(result.state_path[-1], goal)
        for index, move in enumerate(result.moves):
            self.assertEqual(result.state_path[index].apply_move(move), result.state_path[index + 1])

    def test_bfs_can_solve_generalized_small_4x4_case_without_per_size_logic(self) -> None:
        goal = PuzzleState.goal(4)
        start = goal.apply_move(LEFT)

        result = breadth_first_search(start)

        self.assertTrue(result.solved)
        self.assertEqual(result.moves, (RIGHT,))
        self.assertEqual(result.solution_length, 1)
        self.assertEqual(apply_moves(start, result.moves), goal)


class AStarSearchTests(unittest.TestCase):
    def assert_solver_reaches_goal(self, start: PuzzleState, result) -> None:
        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertEqual(apply_moves(start, result.moves), PuzzleState.goal(start.size))
        self.assertEqual(result.state_path[0], start)
        self.assertEqual(result.state_path[-1], PuzzleState.goal(start.size))

    def test_a_star_algorithms_match_bfs_lengths_on_modest_3x3_cases(self) -> None:
        goal = PuzzleState.goal(3)
        starts = (
            goal,
            goal.apply_move(LEFT),
            goal.apply_move(LEFT).apply_move(UP),
            goal.apply_move(LEFT).apply_move(UP).apply_move(LEFT),
        )

        for start in starts:
            with self.subTest(start=start.tiles):
                bfs = breadth_first_search(start)
                misplaced = a_star_misplaced(start)
                manhattan = a_star_manhattan(start)

                self.assert_solver_reaches_goal(start, bfs)
                self.assert_solver_reaches_goal(start, misplaced)
                self.assert_solver_reaches_goal(start, manhattan)
                self.assertEqual(misplaced.solution_length, bfs.solution_length)
                self.assertEqual(manhattan.solution_length, bfs.solution_length)

    def test_a_star_misplaced_handles_invalid_and_unsolvable_input(self) -> None:
        invalid = a_star_misplaced((1, 2, 3, 4, 5, 6, 7, 7, 0))
        unsolvable = a_star_misplaced((1, 2, 3, 4, 5, 6, 8, 7, 0))

        self.assertFalse(invalid.solved)
        self.assertEqual(invalid.status, STATUS_INVALID)
        self.assertEqual(invalid.expanded_states, 0)

        self.assertFalse(unsolvable.solved)
        self.assertEqual(unsolvable.status, STATUS_UNSOLVABLE)
        self.assertEqual(unsolvable.expanded_states, 0)

    def test_a_star_manhattan_handles_invalid_and_unsolvable_input(self) -> None:
        invalid = a_star_manhattan((1, 2, 3, 4, 5, 6, 7, 7, 0))
        unsolvable = a_star_manhattan((1, 2, 3, 4, 5, 6, 8, 7, 0))

        self.assertFalse(invalid.solved)
        self.assertEqual(invalid.status, STATUS_INVALID)
        self.assertEqual(invalid.expanded_states, 0)

        self.assertFalse(unsolvable.solved)
        self.assertEqual(unsolvable.status, STATUS_UNSOLVABLE)
        self.assertEqual(unsolvable.expanded_states, 0)

    def test_a_star_already_solved_state_has_zero_expansions(self) -> None:
        goal = PuzzleState.goal(3)

        misplaced = a_star_misplaced(goal)
        manhattan = a_star_manhattan(goal)

        self.assertEqual(misplaced.solution_length, 0)
        self.assertEqual(misplaced.moves, ())
        self.assertEqual(misplaced.expanded_states, 0)

        self.assertEqual(manhattan.solution_length, 0)
        self.assertEqual(manhattan.moves, ())
        self.assertEqual(manhattan.expanded_states, 0)


if __name__ == "__main__":
    unittest.main()
