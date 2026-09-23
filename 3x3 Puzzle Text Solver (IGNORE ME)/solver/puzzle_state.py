"""Core generalized puzzle-state model for the sliding-tile project.

File purpose:
    Provide reusable state construction, goal construction, coordinate
    conversion, legal movement, successor generation, and reviewer-readable
    formatting for 3x3, 4x4, and 5x5 sliding-tile boards.

Assignment requirements addressed:
    R02: Python sliding-tile solver foundation.
    R03: Generalized N x N board design.
    R04: Lower-right blank goal state.
    R05: Immutable flat tuple board representation.
    R06: Blank-movement move naming convention.

Graded submission artifact:
    Supporting module used by the required root artifact `02_python_solver.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .constants import BLANK, DOWN, LEFT, MOVES, RIGHT, SUPPORTED_SIZES, UP
from .validation import InvalidPuzzleStateError, infer_size, validate_board

_MOVE_DELTAS = {
    UP: (-1, 0),
    DOWN: (1, 0),
    LEFT: (0, -1),
    RIGHT: (0, 1),
}


def index_to_position(index: int, size: int) -> tuple[int, int]:
    """Convert a flat tuple index to a zero-based `(row, column)` pair."""
    if size not in SUPPORTED_SIZES:
        raise ValueError("Board size must be 3, 4, or 5.")
    if not 0 <= index < size * size:
        raise ValueError("Index is outside the board.")
    return index // size, index % size


def position_to_index(row: int, column: int, size: int) -> int:
    """Convert a zero-based `(row, column)` pair to a flat tuple index."""
    if size not in SUPPORTED_SIZES:
        raise ValueError("Board size must be 3, 4, or 5.")
    if not (0 <= row < size and 0 <= column < size):
        raise ValueError("Position is outside the board.")
    return row * size + column


def create_goal_state(size: int) -> tuple[int, ...]:
    """Return the tuple goal state for a supported N x N board."""
    if size not in SUPPORTED_SIZES:
        raise ValueError("Goal states are supported only for 3x3, 4x4, and 5x5.")

    # ASSIGNMENT REQUIREMENT R04 — LOWER-RIGHT BLANK GOAL
    # The goal is ascending numbered tiles followed by the internal blank value 0.
    return tuple(range(1, size * size)) + (BLANK,)


def format_board(tiles: Iterable[int], size: int | None = None) -> str:
    """Format a flat board as rows for debugging and reviewer inspection."""
    board = tuple(tiles)
    resolved_size = size if size is not None else infer_size(len(board))
    if len(board) != resolved_size * resolved_size:
        raise ValueError("Board length does not match the supplied board size.")

    width = len(str(resolved_size * resolved_size - 1))
    rows = []
    for row in range(resolved_size):
        start = row * resolved_size
        values = board[start : start + resolved_size]
        rows.append(
            " ".join("_".rjust(width) if value == BLANK else str(value).rjust(width) for value in values)
        )
    return "\n".join(rows)


@dataclass(frozen=True)
class PuzzleState:
    """Immutable sliding-tile puzzle state.

    # ASSIGNMENT REQUIREMENT R05 — BOARD REPRESENTATION
    # The underlying board is an immutable flat tuple of integers. This makes
    # states hashable and appropriate for future search visited/discovered sets.
    """

    tiles: tuple[int, ...]
    size: int | None = None

    def __post_init__(self) -> None:
        validated = validate_board(self.tiles, self.size)
        object.__setattr__(self, "tiles", validated.tiles)
        object.__setattr__(self, "size", validated.size)

    @classmethod
    def goal(cls, size: int) -> "PuzzleState":
        return cls(create_goal_state(size), size)

    @property
    def dimension(self) -> int:
        return self.size

    def blank_index(self) -> int:
        return self.tiles.index(BLANK)

    def blank_position(self) -> tuple[int, int]:
        return index_to_position(self.blank_index(), self.size)

    def index_to_position(self, index: int) -> tuple[int, int]:
        return index_to_position(index, self.size)

    def position_to_index(self, row: int, column: int) -> int:
        return position_to_index(row, column, self.size)

    def is_goal(self) -> bool:
        return self.tiles == create_goal_state(self.size)

    def legal_moves(self) -> tuple[str, ...]:
        """Return legal blank-movement names from the current blank location."""
        blank_row, blank_column = self.blank_position()
        legal: list[str] = []

        # ASSIGNMENT REQUIREMENT R03 — GENERALIZED N x N BOARD DESIGN
        # Movement is derived from N, row, and column arithmetic rather than
        # fixed 3x3 indices or separate 3x3/4x4/5x5 implementations.
        for move in MOVES:
            row_delta, column_delta = _MOVE_DELTAS[move]
            target_row = blank_row + row_delta
            target_column = blank_column + column_delta
            if 0 <= target_row < self.size and 0 <= target_column < self.size:
                legal.append(move)

        return tuple(legal)

    def can_apply_move(self, move: str) -> bool:
        return move in self.legal_moves()

    def apply_move(self, move: str) -> "PuzzleState":
        """Apply a legal blank movement and return the resulting state."""
        if move not in MOVES:
            raise ValueError(f"Unknown move {move!r}. Expected one of {MOVES}.")
        if not self.can_apply_move(move):
            raise ValueError(f"Move {move!r} is not legal from the current blank position.")

        # ASSIGNMENT REQUIREMENT R06 — MOVE NAMING / SEMANTICS
        # UP/DOWN/LEFT/RIGHT describe movement of the blank. The numbered tile
        # swapped with the blank visually moves in the opposite direction.
        blank_row, blank_column = self.blank_position()
        row_delta, column_delta = _MOVE_DELTAS[move]
        target_row = blank_row + row_delta
        target_column = blank_column + column_delta
        blank_index = self.blank_index()
        target_index = self.position_to_index(target_row, target_column)

        next_tiles = list(self.tiles)
        next_tiles[blank_index], next_tiles[target_index] = (
            next_tiles[target_index],
            next_tiles[blank_index],
        )
        return PuzzleState(tuple(next_tiles), self.size)

    def successors(self) -> tuple[tuple[str, "PuzzleState"], ...]:
        """Generate all legal successor states in documented move-name order."""
        return tuple((move, self.apply_move(move)) for move in self.legal_moves())

    def format(self) -> str:
        return format_board(self.tiles, self.size)
