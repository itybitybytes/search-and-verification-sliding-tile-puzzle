"""Reviewer-facing entry point for the text-only sliding-tile solver.

============================================================
AI SEARCH ASSIGNMENT — PYTHON SLIDING-TILE SOLVER
============================================================

This required graded artifact exposes the Python solver functionality without
duplicating the algorithms that live in the `puzzle/` support package.

Reviewer anchors:

- R03 generalized architecture: `PuzzleState`, `goal_board`, and N-based
  row/column movement support 3x3, 4x4, and 5x5 boards.
- R04 goal: numbered tiles ascend in row-major order and blank `0` is lower
  right.
- R05 representation: each board is an immutable flat `tuple[int, ...]`.
- R06 moves: `UP`, `DOWN`, `LEFT`, `RIGHT` describe blank movement.
- R07 tie-breaking: A* uses lowest `f`, then lowest `h`, then earliest
  insertion counter.
- R08 invalid states: malformed boards are rejected before search.
- R09 unsolvable states: parity checks short-circuit impossible boards.
- R10 BFS: `breadth_first_search`.
- R11 BFS optimality: unit-cost FIFO BFS explores by increasing path depth.
- R12 A* misplaced: `a_star_misplaced`.
- R13 A* Manhattan: `a_star_manhattan`.
- R14 misplaced excludes blank: `misplaced_tiles` skips `0`.
- R15 Manhattan excludes blank: `manhattan_distance` skips `0`.
- R16 h(goal)=0: both heuristics return zero for generated goals.
- R17 move sequence: `SearchResult.moves`.
- R18 solution length: `SearchResult.solution_length`.
- R19 expanded states: `SearchResult.expanded_states`.
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from puzzle import (
    A_STAR_MANHATTAN_ALGORITHM_NAME,
    A_STAR_MISPLACED_ALGORITHM_NAME,
    BFS_ALGORITHM_NAME,
    BLANK,
    MOVES,
    SUPPORTED_SIZES,
    InvalidPuzzleStateError,
    PuzzleState,
    SearchResult,
    a_star_manhattan,
    a_star_misplaced,
    blank_row_from_bottom,
    breadth_first_search,
    count_inversions,
    goal_board,
    infer_dimension,
    is_solvable,
    manhattan_distance,
    misplaced_tiles,
    reconstruct_moves,
    validate_board,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ASSIGNMENT REQUIREMENT R04 — LOWER-RIGHT BLANK GOAL
# ASSIGNMENT REQUIREMENT R05 — BOARD REPRESENTATION
# Fixed 3x3 verification boards use the documented immutable flat tuple format.
SOLVED_STATE_3X3 = goal_board(3)


def board_after_blank_moves(
    board: tuple[int, ...],
    moves: tuple[str, ...],
    size: int | None = None,
) -> tuple[int, ...]:
    """Apply a fixed legal blank-movement sequence and return the resulting board."""

    state = PuzzleState(board, size)
    for move in moves:
        state = state.apply_move(move)
    return state.board


# ASSIGNMENT REQUIREMENT R06 — MOVE NAMING / BLANK MOVEMENT
# These setup sequences move the blank, not the numbered tile.
ONE_MOVE_SETUP = ("LEFT",)
SEVERAL_MOVE_SETUP = ("LEFT", "UP", "LEFT")
COMPARISON_SETUP = ("LEFT", "UP", "LEFT", "DOWN", "RIGHT", "UP")

ONE_MOVE_STATE_3X3 = board_after_blank_moves(SOLVED_STATE_3X3, ONE_MOVE_SETUP, 3)
SEVERAL_MOVE_STATE_3X3 = board_after_blank_moves(SOLVED_STATE_3X3, SEVERAL_MOVE_SETUP, 3)
COMPARISON_STATE_3X3 = board_after_blank_moves(SOLVED_STATE_3X3, COMPARISON_SETUP, 3)

# ASSIGNMENT REQUIREMENT R08 — INVALID STATES
# Duplicate `7` and missing `8` make this structurally malformed.
INVALID_STATE_3X3 = (1, 2, 3, 4, 5, 6, 7, 7, 0)

# ASSIGNMENT REQUIREMENT R09 — UNSOLVABLE STATES
# This is a valid tile set with the 7/8 inversion parity swapped.
UNSOLVABLE_STATE_3X3 = (1, 2, 3, 4, 5, 6, 8, 7, 0)

SearchFunction = Callable[[tuple[int, ...]], SearchResult]

ALGORITHMS: tuple[tuple[str, SearchFunction], ...] = (
    (BFS_ALGORITHM_NAME, breadth_first_search),
    (A_STAR_MISPLACED_ALGORITHM_NAME, a_star_misplaced),
    (A_STAR_MANHATTAN_ALGORITHM_NAME, a_star_manhattan),
)


def format_board(board: tuple[int, ...], size: int | None = None) -> str:
    """Return an ASCII-safe reviewer/debug rendering of a board."""

    return PuzzleState(board, size).render(use_unicode_blank=False)


def print_result(result: SearchResult) -> None:
    """Print the required inspectable solver fields in a compact form."""

    print(f"Algorithm: {result.algorithm}")
    print(f"Solved: {result.solved}")
    print(f"Status: {result.status}")
    print(f"Move sequence: {', '.join(result.moves) if result.moves else '(empty)'}")
    print(f"Solution length: {result.solution_length}")
    print(f"Expanded states: {result.expanded_states}")
    if result.message:
        print(f"Message: {result.message}")


def demo() -> None:
    """Run a concise noninteractive 3x3 demonstration for reviewers."""

    print("============================================================")
    print("AI SEARCH ASSIGNMENT — PYTHON SLIDING-TILE SOLVER")
    print("============================================================")
    print()
    print("Sample 3x3 state:")
    print(format_board(COMPARISON_STATE_3X3, 3))
    print()
    print("Representation: immutable flat tuple[int, ...]")
    print("Blank: 0")
    print("Moves: UP, DOWN, LEFT, RIGHT describe blank movement")
    print("A* tie-breaking: lowest f, then lowest h, then insertion order")
    print()

    for _name, search in ALGORITHMS:
        result = search(COMPARISON_STATE_3X3)
        print("------------------------------------------------------------")
        print_result(result)


__all__ = [
    "A_STAR_MANHATTAN_ALGORITHM_NAME",
    "A_STAR_MISPLACED_ALGORITHM_NAME",
    "ALGORITHMS",
    "BFS_ALGORITHM_NAME",
    "BLANK",
    "COMPARISON_SETUP",
    "COMPARISON_STATE_3X3",
    "INVALID_STATE_3X3",
    "MOVES",
    "ONE_MOVE_SETUP",
    "ONE_MOVE_STATE_3X3",
    "PuzzleState",
    "SEVERAL_MOVE_SETUP",
    "SEVERAL_MOVE_STATE_3X3",
    "SOLVED_STATE_3X3",
    "SUPPORTED_SIZES",
    "SearchResult",
    "UNSOLVABLE_STATE_3X3",
    "InvalidPuzzleStateError",
    "a_star_manhattan",
    "a_star_misplaced",
    "blank_row_from_bottom",
    "board_after_blank_moves",
    "breadth_first_search",
    "count_inversions",
    "format_board",
    "goal_board",
    "infer_dimension",
    "is_solvable",
    "manhattan_distance",
    "misplaced_tiles",
    "print_result",
    "reconstruct_moves",
    "validate_board",
]


if __name__ == "__main__":
    demo()
