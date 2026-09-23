"""Admissible heuristics for N x N sliding-tile puzzles.

File purpose:
    Provide misplaced-tile and Manhattan-distance heuristic functions for the
    future and current A* search variants.

Assignment requirements addressed:
    R14 misplaced tiles ignores blank.
    R15 Manhattan distance ignores blank.
    R16 heuristics equal zero at goal.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver.
"""

from __future__ import annotations

from typing import Iterable

from .model import goal_board
from .validation import BLANK, validate_board


def misplaced_tiles(board: Iterable[int], size: int | None = None) -> int:
    """Count nonblank tiles that are not in their goal positions.

    # ASSIGNMENT REQUIREMENT R14 — MISPLACED IGNORES BLANK
    # The internal blank value 0 is skipped and never contributes to this count.
    #
    # ASSIGNMENT REQUIREMENT R16 — HEURISTICS EQUAL ZERO AT GOAL
    # When the board equals the generated goal board, no numbered tile is out of
    # place, so the returned value is 0.
    """

    board_tuple, validated_size = validate_board(board, size)
    goal = goal_board(validated_size)
    return sum(
        1
        for index, tile in enumerate(board_tuple)
        if tile != BLANK and tile != goal[index]
    )


def manhattan_distance(board: Iterable[int], size: int | None = None) -> int:
    """Sum row/column distance from each nonblank tile to its goal location.

    # ASSIGNMENT REQUIREMENT R15 — MANHATTAN IGNORES BLANK
    # The blank 0 is excluded before any row/column distance is calculated.
    #
    # ASSIGNMENT REQUIREMENT R16 — HEURISTICS EQUAL ZERO AT GOAL
    # Goal positions are generated from N rather than hard-coded for 3x3, so
    # this returns 0 for valid 3x3, 4x4, and 5x5 goal boards.
    """

    board_tuple, validated_size = validate_board(board, size)
    goal_positions = {
        tile: (index // validated_size, index % validated_size)
        for index, tile in enumerate(goal_board(validated_size))
        if tile != BLANK
    }

    total = 0
    for index, tile in enumerate(board_tuple):
        if tile == BLANK:
            continue
        current_row = index // validated_size
        current_column = index % validated_size
        goal_row, goal_column = goal_positions[tile]
        total += abs(current_row - goal_row) + abs(current_column - goal_column)
    return total
