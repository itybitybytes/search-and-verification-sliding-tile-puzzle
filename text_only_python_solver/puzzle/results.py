"""Shared search results and path reconstruction.

File purpose:
    Provide one result structure and one reusable path-reconstruction helper
    for BFS and future A* implementations.

Assignment requirements addressed:
    R17 returned move sequence.
    R18 solution length.
    R19 expanded states.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import PuzzleState


@dataclass(frozen=True)
class SearchResult:
    """Structured result shared by all search algorithms.

    # ASSIGNMENT REQUIREMENT R17 — RETURNED MOVE SEQUENCE
    # The `moves` tuple is directly inspectable and uses UP/DOWN/LEFT/RIGHT
    # blank-movement names.
    #
    # ASSIGNMENT REQUIREMENT R18 — SOLUTION LENGTH
    # For solved results, solution_length is normalized to len(moves).
    #
    # ASSIGNMENT REQUIREMENT R19 — EXPANDED STATES
    # expanded_states stores the number of popped states whose successors were
    # actually generated or examined.
    """

    algorithm: str
    solved: bool
    moves: tuple[str, ...] = field(default_factory=tuple)
    solution_length: int = 0
    expanded_states: int = 0
    status: str = "not_started"
    message: str = ""

    def __post_init__(self) -> None:
        if self.expanded_states < 0:
            raise ValueError("expanded_states cannot be negative.")
        if self.solved:
            object.__setattr__(self, "moves", tuple(self.moves))
            object.__setattr__(self, "solution_length", len(self.moves))
            object.__setattr__(self, "status", "solved")
        elif self.solution_length < 0:
            raise ValueError("solution_length cannot be negative.")


def reconstruct_moves(
    parents: dict[PuzzleState, tuple[PuzzleState | None, str | None]],
    goal_state: PuzzleState,
) -> tuple[str, ...]:
    """Reconstruct the ordered blank-movement path from start to goal."""

    moves_reversed: list[str] = []
    current = goal_state

    while True:
        parent, move = parents[current]
        if parent is None:
            break
        if move is None:
            raise ValueError("Non-root parent entry is missing a move.")
        moves_reversed.append(move)
        current = parent

    return tuple(reversed(moves_reversed))


def solved_result(algorithm: str, moves: tuple[str, ...], expanded_states: int) -> SearchResult:
    return SearchResult(
        algorithm=algorithm,
        solved=True,
        moves=moves,
        expanded_states=expanded_states,
        message="Puzzle solved.",
    )


def invalid_result(algorithm: str, message: str) -> SearchResult:
    return SearchResult(
        algorithm=algorithm,
        solved=False,
        status="invalid",
        message=message,
    )


def unsolvable_result(algorithm: str) -> SearchResult:
    return SearchResult(
        algorithm=algorithm,
        solved=False,
        status="unsolvable",
        message="Puzzle is structurally valid but unsolvable.",
    )
