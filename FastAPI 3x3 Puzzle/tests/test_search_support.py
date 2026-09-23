"""Tests for shared search-result infrastructure."""

from __future__ import annotations

import unittest

from solver import (
    RIGHT,
    STATUS_INVALID,
    STATUS_SOLVED,
    STATUS_UNSOLVABLE,
    ExpandedCounter,
    PuzzleState,
    SearchResult,
    SearchStep,
    make_invalid_result,
    make_solved_result,
    make_unsolvable_result,
    reconstruct_path,
)


class SearchSupportTests(unittest.TestCase):
    def test_already_solved_result_has_empty_move_sequence(self) -> None:
        goal = PuzzleState.goal(3)

        result = make_solved_result("TEST", goal, goal, {}, expanded_states=0)

        self.assertTrue(result.solved)
        self.assertEqual(result.status, STATUS_SOLVED)
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertEqual(result.expanded_states, 0)
        self.assertEqual(result.state_path, (goal,))

    def test_reconstruct_path_returns_ordered_blank_moves_and_states(self) -> None:
        goal = PuzzleState.goal(3)
        start = goal.apply_move("LEFT")
        predecessors = {
            goal: SearchStep(previous_state=start, move=RIGHT),
        }

        moves, states = reconstruct_path(start, goal, predecessors)

        self.assertEqual(moves, (RIGHT,))
        self.assertEqual(states, (start, goal))
        self.assertEqual(start.apply_move(moves[0]), goal)

    def test_make_solved_result_sets_solution_length_from_moves(self) -> None:
        goal = PuzzleState.goal(3)
        start = goal.apply_move("LEFT")
        predecessors = {
            goal: SearchStep(previous_state=start, move=RIGHT),
        }

        result = make_solved_result("TEST", start, goal, predecessors, expanded_states=1)

        self.assertTrue(result.solved)
        self.assertEqual(result.moves, (RIGHT,))
        self.assertEqual(result.solution_length, 1)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertEqual(result.expanded_states, 1)
        self.assertEqual(result.state_path, (start, goal))

    def test_search_result_rejects_solved_length_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            SearchResult(
                algorithm="TEST",
                solved=True,
                moves=(RIGHT,),
                solution_length=2,
                status=STATUS_SOLVED,
            )

    def test_search_result_rejects_unknown_move_name(self) -> None:
        with self.assertRaises(ValueError):
            SearchResult(
                algorithm="TEST",
                solved=True,
                moves=("TILE_UP",),
                solution_length=1,
                status=STATUS_SOLVED,
            )

    def test_invalid_and_unsolvable_results_use_standard_statuses(self) -> None:
        invalid = make_invalid_result("TEST", "bad board")
        goal = PuzzleState.goal(3)
        unsolvable = make_unsolvable_result("TEST", goal.apply_move("LEFT"), goal)

        self.assertFalse(invalid.solved)
        self.assertEqual(invalid.status, STATUS_INVALID)
        self.assertEqual(invalid.moves, ())
        self.assertEqual(invalid.solution_length, 0)

        self.assertFalse(unsolvable.solved)
        self.assertEqual(unsolvable.status, STATUS_UNSOLVABLE)
        self.assertEqual(unsolvable.moves, ())
        self.assertEqual(unsolvable.solution_length, 0)

    def test_expanded_counter_records_successor_generation_only(self) -> None:
        counter = ExpandedCounter()

        self.assertEqual(counter.count, 0)
        counter.record_successor_generation()
        counter.record_successor_generation()

        self.assertEqual(counter.count, 2)

    def test_reconstruct_path_rejects_broken_predecessor_chain(self) -> None:
        goal = PuzzleState.goal(3)
        start = goal.apply_move("LEFT")

        with self.assertRaises(ValueError):
            reconstruct_path(start, goal, {})


if __name__ == "__main__":
    unittest.main()
