"""Validation and solvability checks for N x N sliding-tile boards.

File purpose:
    Reject malformed puzzle boards and identify valid-but-unsolvable states.

Assignment requirements addressed:
    R08 invalid state handling.
    R09 unsolvable state handling.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver.
"""

from __future__ import annotations

from math import isqrt
from typing import Iterable

BLANK = 0
SUPPORTED_SIZES = frozenset({3, 4, 5})


class InvalidPuzzleStateError(ValueError):
    """Raised when a board violates the documented tuple/int representation."""


def _coerce_tuple(board: Iterable[int]) -> tuple[int, ...]:
    try:
        coerced = tuple(board)
    except TypeError as exc:
        raise InvalidPuzzleStateError("Board must be an iterable of integers.") from exc

    non_int_values = [
        value for value in coerced if isinstance(value, bool) or not isinstance(value, int)
    ]
    if non_int_values:
        raise InvalidPuzzleStateError(
            f"Board values must be integers; invalid value(s): {non_int_values}."
        )
    return coerced


def infer_dimension(board: Iterable[int]) -> int:
    """Infer N from a flat N*N board whose length is a supported square."""

    board_tuple = _coerce_tuple(board)
    length = len(board_tuple)
    size = isqrt(length)
    if size * size != length:
        raise InvalidPuzzleStateError(
            f"Board length {length} does not form a square N x N board."
        )
    if size not in SUPPORTED_SIZES:
        supported = ", ".join(str(value) for value in sorted(SUPPORTED_SIZES))
        raise InvalidPuzzleStateError(
            f"Board size {size}x{size} is unsupported; supported sizes are {supported}."
        )
    return size


def validate_board(board: Iterable[int], size: int | None = None) -> tuple[tuple[int, ...], int]:
    """Validate representation, length, blank count, and exact tile set.

    # ASSIGNMENT REQUIREMENT R08 — INVALID STATE HANDLING
    # Malformed boards raise a controlled error before any future search code
    # can place the state into BFS or A* frontiers.
    """

    board_tuple = _coerce_tuple(board)

    if size is None:
        validated_size = infer_dimension(board_tuple)
    else:
        if isinstance(size, bool) or not isinstance(size, int):
            raise InvalidPuzzleStateError("Board size must be an integer.")
        if size not in SUPPORTED_SIZES:
            supported = ", ".join(str(value) for value in sorted(SUPPORTED_SIZES))
            raise InvalidPuzzleStateError(
                f"Board size {size}x{size} is unsupported; supported sizes are {supported}."
            )
        validated_size = size

    expected_length = validated_size * validated_size
    if len(board_tuple) != expected_length:
        raise InvalidPuzzleStateError(
            f"Board length {len(board_tuple)} does not match {validated_size}x{validated_size}."
        )

    blank_count = board_tuple.count(BLANK)
    if blank_count != 1:
        raise InvalidPuzzleStateError(
            f"Board must contain exactly one blank value 0; found {blank_count}."
        )

    seen = set()
    duplicates = []
    for value in board_tuple:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    if duplicates:
        raise InvalidPuzzleStateError(f"Board contains duplicate tile value(s): {duplicates}.")

    expected_values = set(range(expected_length))
    actual_values = set(board_tuple)
    missing = sorted(expected_values - actual_values)
    unexpected = sorted(actual_values - expected_values)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing required tile value(s): {missing}")
        if unexpected:
            details.append(f"out-of-range tile value(s): {unexpected}")
        raise InvalidPuzzleStateError("Board tile set mismatch; " + "; ".join(details) + ".")

    return board_tuple, validated_size


def count_inversions(board: Iterable[int], size: int | None = None) -> int:
    """Count pairwise inversions among numbered tiles, ignoring the blank."""

    board_tuple, _ = validate_board(board, size)
    tiles = [value for value in board_tuple if value != BLANK]
    inversions = 0
    for index, value in enumerate(tiles):
        inversions += sum(1 for later in tiles[index + 1 :] if value > later)
    return inversions


def blank_row_from_bottom(board: Iterable[int], size: int | None = None) -> int:
    """Return the blank row number counted from the bottom, starting at 1."""

    board_tuple, validated_size = validate_board(board, size)
    blank_index = board_tuple.index(BLANK)
    blank_row_from_top = blank_index // validated_size
    return validated_size - blank_row_from_top


def is_solvable(board: Iterable[int], size: int | None = None) -> bool:
    """Return whether a valid board can reach the lower-right blank goal.

    # ASSIGNMENT REQUIREMENT R09 — UNSOLVABLE STATE HANDLING
    # For odd-width boards such as 3x3 and 5x5, the blank's row parity does not
    # change the reachability rule: an even inversion count is solvable.
    #
    # For even-width boards such as 4x4, moving the blank across rows changes
    # the parity relationship. With the selected lower-right blank goal, a board
    # is solvable when inversions + blank_row_from_bottom is odd.
    """

    board_tuple, validated_size = validate_board(board, size)
    inversions = count_inversions(board_tuple, validated_size)

    if validated_size % 2 == 1:
        return inversions % 2 == 0

    row_from_bottom = blank_row_from_bottom(board_tuple, validated_size)
    return (inversions + row_from_bottom) % 2 == 1
