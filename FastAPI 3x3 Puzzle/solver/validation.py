"""Validation helpers for sliding-tile puzzle states.

File purpose:
    Reject malformed boards before they can enter search algorithms.

Assignment requirements addressed:
    R08: Invalid puzzle state handling.

Graded submission artifact:
    Supporting module used by the required root artifact `02_python_solver.py`.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import isqrt
from typing import Iterable

from .constants import BLANK, SUPPORTED_SIZES


class InvalidPuzzleStateError(ValueError):
    """Raised when a board is malformed rather than merely unsolvable."""


@dataclass(frozen=True)
class ValidatedBoard:
    """Normalized valid board data."""

    tiles: tuple[int, ...]
    size: int


def infer_size(tile_count: int) -> int:
    """Infer a supported square board size from a flat board length."""
    size = isqrt(tile_count)
    if size * size != tile_count or size not in SUPPORTED_SIZES:
        raise InvalidPuzzleStateError(
            "Board must contain N*N positions for exactly one supported size: "
            "3x3, 4x4, or 5x5."
        )
    return size


def validate_board(tiles: Iterable[int], size: int | None = None) -> ValidatedBoard:
    """Validate and normalize a sliding-tile board.

    # ASSIGNMENT REQUIREMENT R08 — INVALID PUZZLE STATE HANDLING
    # Malformed boards are rejected before future BFS/A* entry points can search
    # them. This validation checks length, square/dimension coherence, exactly
    # one blank, duplicate values, missing values, and out-of-range values.
    """
    try:
        normalized_tiles = tuple(tiles)
    except TypeError as exc:
        raise InvalidPuzzleStateError("Board must be an iterable of integers.") from exc

    resolved_size = size if size is not None else infer_size(len(normalized_tiles))

    if resolved_size not in SUPPORTED_SIZES:
        raise InvalidPuzzleStateError("Board size must be exactly 3, 4, or 5.")

    expected_length = resolved_size * resolved_size
    if len(normalized_tiles) != expected_length:
        raise InvalidPuzzleStateError(
            f"Board length must be {expected_length} for a {resolved_size}x{resolved_size} board."
        )

    if not all(isinstance(tile, int) for tile in normalized_tiles):
        raise InvalidPuzzleStateError("Every board position must contain an integer.")

    counts = Counter(normalized_tiles)
    expected_values = set(range(expected_length))
    actual_values = set(normalized_tiles)

    blank_count = counts.get(BLANK, 0)
    if blank_count != 1:
        raise InvalidPuzzleStateError("Board must contain exactly one blank value, represented by 0.")

    duplicate_values = sorted(value for value, count in counts.items() if count > 1)
    if duplicate_values:
        raise InvalidPuzzleStateError(f"Board contains duplicate tile value(s): {duplicate_values}.")

    unexpected_values = sorted(actual_values - expected_values)
    if unexpected_values:
        raise InvalidPuzzleStateError(
            f"Board contains unexpected or out-of-range tile value(s): {unexpected_values}."
        )

    missing_values = sorted(expected_values - actual_values)
    if missing_values:
        raise InvalidPuzzleStateError(f"Board is missing required tile value(s): {missing_values}.")

    return ValidatedBoard(normalized_tiles, resolved_size)
