"""============================================================
AI SEARCH ASSIGNMENT — RUNNABLE SOLVER VERIFICATION
============================================================

Required top-level graded submission artifact.

Run directly:
    python 03_verify_solver.py

This script exercises the fixed 3x3 verification cases and prints real results
from the current BFS, A* misplaced, and A* Manhattan implementations.
"""

from __future__ import annotations

import sys
from typing import Callable

from solver import (
    ASTAR_MANHATTAN_ALGORITHM_NAME,
    ASTAR_MISPLACED_ALGORITHM_NAME,
    BFS_ALGORITHM_NAME,
    COMPARISON_BOARD,
    INVALID_BOARD,
    ONE_MOVE_BOARD,
    SEVERAL_MOVE_BOARD,
    SOLVED_BOARD,
    STATUS_INVALID,
    STATUS_SOLVED,
    STATUS_UNSOLVABLE,
    UNSOLVABLE_BOARD,
    VERIFICATION_SIZE,
    PuzzleState,
    SearchResult,
    a_star_manhattan,
    a_star_misplaced,
    breadth_first_search,
    format_board,
    manhattan_distance,
    misplaced_tiles,
)

SearchFunction = Callable[[tuple[int, ...], int | None], SearchResult]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ALGORITHMS: tuple[tuple[str, SearchFunction], ...] = (
    (BFS_ALGORITHM_NAME, breadth_first_search),
    (ASTAR_MISPLACED_ALGORITHM_NAME, a_star_misplaced),
    (ASTAR_MANHATTAN_ALGORITHM_NAME, a_star_manhattan),
)


def print_section(title: str) -> None:
    print("=" * 60)
    print(title)
    print("=" * 60)


def format_moves(moves: tuple[str, ...]) -> str:
    return ", ".join(moves) if moves else "(none)"


def print_board(label: str, board: tuple[int, ...]) -> None:
    print(label)
    print(format_board(board, VERIFICATION_SIZE))


def verify_solution(board: tuple[int, ...], result: SearchResult) -> None:
    """Assert returned moves are legal and lead to the lower-right blank goal."""

    assert result.solved, f"{result.algorithm} did not solve a solvable board."
    assert result.status == STATUS_SOLVED
    assert result.solution_length == len(result.moves)

    current = PuzzleState(board, VERIFICATION_SIZE)
    for move in result.moves:
        assert move in current.legal_moves(), f"{result.algorithm} returned illegal move {move!r}."
        current = current.apply_move(move)

    assert current == PuzzleState.goal(VERIFICATION_SIZE), (
        f"{result.algorithm} moves did not reach the goal."
    )


def run_successful_case(
    title: str,
    board: tuple[int, ...],
    expected_length: int | None = None,
) -> tuple[SearchResult, ...]:
    # ASSIGNMENT REQUIREMENTS R20-R23, R26, R27
    # Each successful verification case prints the start state, algorithm name,
    # inspectable returned move sequence, solution length, and expanded states.
    print_section(title)
    print_board("Starting state:", board)

    results = []
    for algorithm_name, search in ALGORITHMS:
        result = search(board, VERIFICATION_SIZE)
        verify_solution(board, result)
        if expected_length is not None:
            assert result.solution_length == expected_length

        print()
        print(f"Algorithm: {algorithm_name}")
        print(f"Move sequence: {format_moves(result.moves)}")
        print(f"Solution length: {result.solution_length}")
        print(f"Expanded states: {result.expanded_states}")
        results.append(result)

    print()
    return tuple(results)


def run_invalid_case() -> None:
    # ASSIGNMENT REQUIREMENT R24
    # The invalid board is malformed, so each algorithm should return a shared
    # structured result with status `invalid` and zero expanded states.
    print_section("TEST 4 — INVALID PUZZLE")
    print_board("Starting state:", INVALID_BOARD)

    for algorithm_name, search in ALGORITHMS:
        result = search(INVALID_BOARD, VERIFICATION_SIZE)
        assert not result.solved
        assert result.status == STATUS_INVALID
        assert result.solution_length == 0
        assert result.moves == ()
        assert result.expanded_states == 0

        print()
        print(f"Algorithm: {algorithm_name}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

    print()


def run_unsolvable_case() -> None:
    # ASSIGNMENT REQUIREMENT R24
    # The unsolvable board has a valid tile set but incorrect parity for the
    # lower-right blank goal, so search should stop before frontier expansion.
    print_section("TEST 5 — UNSOLVABLE PUZZLE")
    print_board("Starting state:", UNSOLVABLE_BOARD)

    for algorithm_name, search in ALGORITHMS:
        result = search(UNSOLVABLE_BOARD, VERIFICATION_SIZE)
        assert not result.solved
        assert result.status == STATUS_UNSOLVABLE
        assert result.solution_length == 0
        assert result.moves == ()
        assert result.expanded_states == 0

        print()
        print(f"Algorithm: {algorithm_name}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

    print()


def run_comparison() -> None:
    # ASSIGNMENT REQUIREMENTS R25-R27
    # The comparison table reports actual solution lengths and expanded-state
    # counts from BFS, A* misplaced, and A* Manhattan on the same modest 3x3
    # solvable board.
    print_section("BFS VS A* COMPARISON")
    print_board("Comparison starting state:", COMPARISON_BOARD)

    results = []
    for _, search in ALGORITHMS:
        result = search(COMPARISON_BOARD, VERIFICATION_SIZE)
        verify_solution(COMPARISON_BOARD, result)
        results.append(result)

    lengths = {result.solution_length for result in results}
    assert len(lengths) == 1, "All three algorithms must return the same optimal length."

    print()
    print("Algorithm | Solution Length | Expanded States")
    print("--- | ---: | ---:")
    for result in results:
        print(f"{result.algorithm} | {result.solution_length} | {result.expanded_states}")
    print()


def main() -> None:
    # ASSIGNMENT REQUIREMENT R20 — RUNNABLE VERIFICATION FILE
    # This file is directly runnable and performs programmatic assertions while
    # printing grader-readable evidence.
    goal = PuzzleState.goal(VERIFICATION_SIZE)

    assert misplaced_tiles(goal) == 0
    assert manhattan_distance(goal) == 0

    run_successful_case("TEST 1 — SOLVED PUZZLE", SOLVED_BOARD, expected_length=0)
    run_successful_case("TEST 2 — ONE MOVE FROM GOAL", ONE_MOVE_BOARD, expected_length=1)
    run_successful_case("TEST 3 — SEVERAL MOVES FROM GOAL", SEVERAL_MOVE_BOARD)
    run_invalid_case()
    run_unsolvable_case()
    run_comparison()

    print("All verification assertions passed.")


if __name__ == "__main__":
    # ASSIGNMENT REQUIREMENT R29 — VERIFICATION SCRIPT SUBMISSION ARTIFACT
    main()
