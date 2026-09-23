"""Heuristic functions for sliding-tile A* search.

File purpose:
    Provide the assignment-required misplaced-tiles and Manhattan-distance
    heuristics without implementing A* search yet.

Assignment requirements addressed:
    R14: Misplaced-tiles heuristic excludes the blank.
    R15: Manhattan-distance heuristic excludes the blank.
    R16: Both heuristics return zero at the goal state.

Graded submission artifact:
    Supporting module used by the required root artifact `02_python_solver.py`.
"""

from __future__ import annotations

from typing import Iterable

from .constants import BLANK
from .puzzle_state import PuzzleState, create_goal_state, index_to_position


def _coerce_state(board: PuzzleState | Iterable[int], size: int | None) -> PuzzleState:
    if isinstance(board, PuzzleState):
        if size is not None and board.size != size:
            raise ValueError("Supplied size does not match the PuzzleState dimension.")
        return board
    return PuzzleState(tuple(board), size)


def _goal_positions(size: int) -> dict[int, tuple[int, int]]:
    goal = create_goal_state(size)
    return {tile: index_to_position(index, size) for index, tile in enumerate(goal)}


def misplaced_tiles(board: PuzzleState | Iterable[int], size: int | None = None) -> int:
    """Count nonblank tiles that are not in their goal positions."""
    state = _coerce_state(board, size)
    goal = create_goal_state(state.size)

    # ASSIGNMENT REQUIREMENT R14 — MISPLACED TILES EXCLUDES BLANK
    # The internal blank value 0 is skipped entirely; only numbered tiles can
    # contribute to the misplaced-tile heuristic.
    misplaced = sum(
        1
        for current, expected in zip(state.tiles, goal)
        if current != BLANK and current != expected
    )

    # ASSIGNMENT REQUIREMENT R16 — HEURISTICS RETURN ZERO AT GOAL
    # Because every nonblank tile matches the generated goal tuple at the goal,
    # this function returns exactly 0 for all supported goal sizes.
    return misplaced


def manhattan_distance(board: PuzzleState | Iterable[int], size: int | None = None) -> int:
    """Sum row/column distance from each nonblank tile to its goal position."""
    state = _coerce_state(board, size)
    goal_positions = _goal_positions(state.size)
    total = 0

    for index, tile in enumerate(state.tiles):
        # ASSIGNMENT REQUIREMENT R15 — MANHATTAN DISTANCE EXCLUDES BLANK
        # The blank has no numbered-tile goal distance and never contributes to
        # the Manhattan sum.
        if tile == BLANK:
            continue
        current_row, current_column = index_to_position(index, state.size)
        goal_row, goal_column = goal_positions[tile]
        total += abs(current_row - goal_row) + abs(current_column - goal_column)

    # ASSIGNMENT REQUIREMENT R16 — HEURISTICS RETURN ZERO AT GOAL
    # Goal coordinates are computed from the generated N x N goal state rather
    # than hard-coded 3x3 positions, so goal states for 3x3, 4x4, and 5x5 all
    # produce a Manhattan value of 0.
    return total
