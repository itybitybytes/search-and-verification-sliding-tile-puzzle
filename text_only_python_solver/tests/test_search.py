from __future__ import annotations

import unittest

from puzzle import PuzzleState, SearchResult, a_star_manhattan, a_star_misplaced, breadth_first_search
from puzzle.results import reconstruct_moves


def apply_moves(board: tuple[int, ...], moves: tuple[str, ...]) -> PuzzleState:
    state = PuzzleState(board)
    for move in moves:
        state = state.apply_move(move)
    return state


class SearchResultTests(unittest.TestCase):
    def test_solved_result_normalizes_solution_length(self) -> None:
        result = SearchResult(
            algorithm="Example",
            solved=True,
            moves=("LEFT", "RIGHT"),
            solution_length=99,
            expanded_states=2,
        )
        self.assertEqual(result.solution_length, 2)
        self.assertEqual(result.status, "solved")

    def test_reconstruct_moves_returns_start_to_goal_order(self) -> None:
        start = PuzzleState((1, 2, 3, 4, 0, 5, 6, 7, 8))
        middle = start.apply_move("DOWN")
        goal = middle.apply_move("RIGHT")
        parents = {
            start: (None, None),
            middle: (start, "DOWN"),
            goal: (middle, "RIGHT"),
        }

        self.assertEqual(reconstruct_moves(parents, goal), ("DOWN", "RIGHT"))


class BreadthFirstSearchTests(unittest.TestCase):
    def test_solved_state_returns_empty_sequence(self) -> None:
        result = breadth_first_search((1, 2, 3, 4, 5, 6, 7, 8, 0))

        self.assertTrue(result.solved)
        self.assertEqual(result.status, "solved")
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.expanded_states, 0)

    def test_one_move_state_returns_minimum_length_one(self) -> None:
        board = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = breadth_first_search(board)

        self.assertTrue(result.solved)
        self.assertEqual(result.moves, ("RIGHT",))
        self.assertEqual(result.solution_length, 1)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertTrue(apply_moves(board, result.moves).is_goal())


class AStarSearchTests(unittest.TestCase):
    def test_a_star_algorithms_match_bfs_solution_lengths(self) -> None:
        boards = (
            (1, 2, 3, 4, 5, 6, 7, 0, 8),
            (1, 2, 3, 0, 4, 6, 7, 5, 8),
            (1, 2, 3, 7, 0, 6, 5, 4, 8),
        )

        for board in boards:
            with self.subTest(board=board):
                bfs_result = breadth_first_search(board)
                misplaced_result = a_star_misplaced(board)
                manhattan_result = a_star_manhattan(board)

                self.assertTrue(bfs_result.solved)
                self.assertTrue(misplaced_result.solved)
                self.assertTrue(manhattan_result.solved)
                self.assertEqual(misplaced_result.solution_length, bfs_result.solution_length)
                self.assertEqual(manhattan_result.solution_length, bfs_result.solution_length)
                self.assertEqual(misplaced_result.solution_length, len(misplaced_result.moves))
                self.assertEqual(manhattan_result.solution_length, len(manhattan_result.moves))
                self.assertTrue(apply_moves(board, misplaced_result.moves).is_goal())
                self.assertTrue(apply_moves(board, manhattan_result.moves).is_goal())

    def test_a_star_handles_already_solved_state(self) -> None:
        for search in (a_star_misplaced, a_star_manhattan):
            with self.subTest(search=search.__name__):
                result = search((1, 2, 3, 4, 5, 6, 7, 8, 0))
                self.assertTrue(result.solved)
                self.assertEqual(result.moves, ())
                self.assertEqual(result.solution_length, 0)
                self.assertEqual(result.expanded_states, 0)

    def test_a_star_returns_invalid_and_unsolvable_results(self) -> None:
        for search in (a_star_misplaced, a_star_manhattan):
            with self.subTest(search=search.__name__):
                invalid = search((1, 2, 3, 4, 5, 6, 7, 7, 0))
                unsolvable = search((1, 2, 3, 4, 5, 6, 8, 7, 0))
                self.assertFalse(invalid.solved)
                self.assertEqual(invalid.status, "invalid")
                self.assertFalse(unsolvable.solved)
                self.assertEqual(unsolvable.status, "unsolvable")
                self.assertEqual(unsolvable.expanded_states, 0)

    def test_several_move_state_returns_expected_minimum_length(self) -> None:
        board = (1, 2, 3, 0, 4, 6, 7, 5, 8)
        result = breadth_first_search(board)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, 3)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertTrue(apply_moves(board, result.moves).is_goal())

    def test_invalid_state_returns_invalid_result(self) -> None:
        result = breadth_first_search((1, 2, 3, 4, 5, 6, 7, 7, 0))

        self.assertFalse(result.solved)
        self.assertEqual(result.status, "invalid")
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertIn("duplicate", result.message)

    def test_unsolvable_state_returns_unsolvable_result(self) -> None:
        result = breadth_first_search((1, 2, 3, 4, 5, 6, 8, 7, 0))

        self.assertFalse(result.solved)
        self.assertEqual(result.status, "unsolvable")
        self.assertEqual(result.moves, ())
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.expanded_states, 0)

    def test_returned_sequence_reaches_goal_for_comparison_style_case(self) -> None:
        board = (1, 2, 3, 7, 0, 6, 5, 4, 8)
        result = breadth_first_search(board)

        self.assertTrue(result.solved)
        self.assertEqual(result.solution_length, 6)
        self.assertEqual(result.solution_length, len(result.moves))
        self.assertTrue(apply_moves(board, result.moves).is_goal())


if __name__ == "__main__":
    unittest.main()
