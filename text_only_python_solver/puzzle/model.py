"""Generalized N x N sliding-tile puzzle state model.

File purpose:
    Represent immutable puzzle states and calculate legal blank movement.

Assignment requirements addressed:
    R02 Python sliding-tile puzzle foundation.
    R03 generalized 3x3/4x4/5x5 design.
    R04 lower-right blank goal.
    R05 tuple board representation.
    R06 blank-movement move names.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .validation import BLANK, SUPPORTED_SIZES, validate_board

MOVES = ("UP", "DOWN", "LEFT", "RIGHT")
_MOVE_DELTAS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


def goal_board(size: int) -> tuple[int, ...]:
    """Create the ascending lower-right blank goal board for a supported size.

    # ASSIGNMENT REQUIREMENT R04 — LOWER-RIGHT BLANK GOAL
    # The goal is tiles 1 through N*N-1 in row-major order followed by blank 0.
    """

    if isinstance(size, bool) or not isinstance(size, int):
        raise ValueError("Board size must be an integer.")
    if size not in SUPPORTED_SIZES:
        supported = ", ".join(str(value) for value in sorted(SUPPORTED_SIZES))
        raise ValueError(f"Board size {size}x{size} is unsupported; supported sizes are {supported}.")
    return tuple(range(1, size * size)) + (BLANK,)


@dataclass(frozen=True)
class PuzzleState:
    """Immutable puzzle state suitable for equality, hashing, and future search.

    # ASSIGNMENT REQUIREMENT R05 — BOARD REPRESENTATION
    # The stored board is an immutable flat tuple[int, ...] in row-major order.
    """

    board: tuple[int, ...] | Iterable[int]
    size: int | None = None

    def __post_init__(self) -> None:
        board_tuple, validated_size = validate_board(self.board, self.size)
        object.__setattr__(self, "board", board_tuple)
        object.__setattr__(self, "size", validated_size)

    @classmethod
    def goal(cls, size: int) -> "PuzzleState":
        return cls(goal_board(size), size)

    @property
    def dimension(self) -> int:
        return int(self.size)

    def is_goal(self) -> bool:
        return self.board == goal_board(self.dimension)

    def blank_index(self) -> int:
        return self.board.index(BLANK)

    def index_to_coordinate(self, index: int) -> tuple[int, int]:
        if index < 0 or index >= len(self.board):
            raise IndexError(f"Index {index} is outside this board.")
        return index // self.dimension, index % self.dimension

    def coordinate_to_index(self, row: int, column: int) -> int:
        if row < 0 or row >= self.dimension or column < 0 or column >= self.dimension:
            raise IndexError(f"Coordinate ({row}, {column}) is outside this board.")
        return row * self.dimension + column

    def legal_moves(self) -> tuple[str, ...]:
        """Return legal blank moves using one dimension-aware implementation.

        # ASSIGNMENT REQUIREMENT R03 — GENERALIZED N x N DESIGN
        # Legal movement is calculated from N, row, and column. There is no
        # separate 3x3, 4x4, or 5x5 movement table.
        #
        # ASSIGNMENT REQUIREMENT R06 — MOVE NAMES / BLANK MOVEMENT
        # UP/DOWN/LEFT/RIGHT describe movement of the blank, not the tile.
        """

        blank_row, blank_column = self.index_to_coordinate(self.blank_index())
        legal = []
        for move in MOVES:
            row_delta, column_delta = _MOVE_DELTAS[move]
            next_row = blank_row + row_delta
            next_column = blank_column + column_delta
            if 0 <= next_row < self.dimension and 0 <= next_column < self.dimension:
                legal.append(move)
        return tuple(legal)

    def apply_move(self, move: str) -> "PuzzleState":
        """Apply one legal blank move and return the next immutable state."""

        if move not in _MOVE_DELTAS:
            raise ValueError(f"Unknown move {move!r}; expected one of {MOVES}.")
        if move not in self.legal_moves():
            raise ValueError(f"Move {move!r} is not legal from this state.")

        blank_row, blank_column = self.index_to_coordinate(self.blank_index())
        row_delta, column_delta = _MOVE_DELTAS[move]
        swap_row = blank_row + row_delta
        swap_column = blank_column + column_delta
        blank_index = self.blank_index()
        swap_index = self.coordinate_to_index(swap_row, swap_column)

        next_board = list(self.board)
        next_board[blank_index], next_board[swap_index] = (
            next_board[swap_index],
            next_board[blank_index],
        )
        return PuzzleState(tuple(next_board), self.dimension)

    def successors(self) -> tuple[tuple[str, "PuzzleState"], ...]:
        return tuple((move, self.apply_move(move)) for move in self.legal_moves())

    def render(self, use_unicode_blank: bool = True) -> str:
        """Render an aligned terminal board, using an axe or ASCII blank."""

        blank_text = "\U0001fa93" if use_unicode_blank else "__"
        labels = [blank_text if value == BLANK else str(value) for value in self.board]
        width = max(len(label) for label in labels)
        rows = []
        for row in range(self.dimension):
            start = row * self.dimension
            row_labels = labels[start : start + self.dimension]
            rows.append(" ".join(label.rjust(width) for label in row_labels))
        return "\n".join(rows)
