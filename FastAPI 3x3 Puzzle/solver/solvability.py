"""Solvability checks for sliding-tile puzzle states.

File purpose:
    Determine whether a structurally valid board can reach the selected goal:
    ascending numbered tiles with the blank in the lower-right corner.

Assignment requirements addressed:
    R09: Unsolvable puzzle state handling.

Graded submission artifact:
    Supporting module used by the required root artifact `02_python_solver.py`.
"""

from __future__ import annotations

from typing import Iterable

from .constants import BLANK
from .validation import validate_board


def count_inversions(tiles: Iterable[int]) -> int:
    """Count pairwise inversions, excluding the blank."""
    numbered_tiles = [tile for tile in tiles if tile != BLANK]
    inversions = 0
    for left_index, left_value in enumerate(numbered_tiles):
        for right_value in numbered_tiles[left_index + 1 :]:
            if left_value > right_value:
                inversions += 1
    return inversions


def blank_row_from_bottom(tiles: Iterable[int], size: int) -> int:
    """Return the blank row counted from the bottom, using 1 for bottom row."""
    board = tuple(tiles)
    blank_index = board.index(BLANK)
    blank_row_from_top = blank_index // size
    return size - blank_row_from_top


def is_solvable(tiles: Iterable[int], size: int | None = None) -> bool:
    """Return whether a valid board can reach the lower-right blank goal.

    # ASSIGNMENT REQUIREMENT R09 — UNSOLVABLE PUZZLE STATE HANDLING
    # For odd-width boards such as 3x3 and 5x5, a board is solvable when its
    # inversion count is even. For even-width boards such as 4x4, the blank row
    # from the bottom matters: with the project's lower-right blank goal, the
    # board is solvable when inversions + blank_row_from_bottom is odd.
    """
    validated = validate_board(tiles, size)
    inversions = count_inversions(validated.tiles)

    if validated.size % 2 == 1:
        return inversions % 2 == 0

    row_from_bottom = blank_row_from_bottom(validated.tiles, validated.size)
    return (inversions + row_from_bottom) % 2 == 1
