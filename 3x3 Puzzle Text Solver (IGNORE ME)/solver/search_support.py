"""Shared search-result and path-reconstruction infrastructure.

File purpose:
    Provide the common result object, predecessor records, path reconstruction,
    and expanded-state counter that future BFS and A* implementations will use.

Assignment requirements addressed:
    R17: Returned move sequence can be inspected.
    R18: Solution length is tracked and tied to the move sequence.
    R19: Expanded states are tracked using the documented definition.

Graded submission artifact:
    Supporting module used by the required root artifact `02_python_solver.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .constants import MOVES
from .puzzle_state import PuzzleState

STATUS_SOLVED = "solved"
STATUS_INVALID = "invalid"
STATUS_UNSOLVABLE = "unsolvable"
STATUS_NOT_SOLVED = "not_solved"


@dataclass(frozen=True)
class SearchStep:
    """One predecessor link used to rebuild a final solution path."""

    previous_state: PuzzleState | None
    move: str | None

    def __post_init__(self) -> None:
        if self.previous_state is None and self.move is not None:
            raise ValueError("A root predecessor step must not include a move.")
        if self.previous_state is not None and self.move not in MOVES:
            raise ValueError(f"Search step move must be one of {MOVES}.")


@dataclass(frozen=True)
class SearchResult:
    """Structured result shared by future BFS and A* solver entry points."""

    algorithm: str
    solved: bool
    moves: tuple[str, ...] = field(default_factory=tuple)
    solution_length: int = 0
    expanded_states: int = 0
    status: str = STATUS_NOT_SOLVED
    message: str = ""
    start_state: PuzzleState | None = None
    goal_state: PuzzleState | None = None
    state_path: tuple[PuzzleState, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        normalized_moves = tuple(self.moves)
        normalized_path = tuple(self.state_path)

        for move in normalized_moves:
            if move not in MOVES:
                raise ValueError(f"Result move {move!r} is not one of {MOVES}.")
        if self.solution_length < 0:
            raise ValueError("Solution length cannot be negative.")
        if self.expanded_states < 0:
            raise ValueError("Expanded-state count cannot be negative.")
        if self.solved and self.status != STATUS_SOLVED:
            raise ValueError("Solved results must use status 'solved'.")
        if self.solved and self.solution_length != len(normalized_moves):
            raise ValueError("Solved results must keep solution_length == len(moves).")
        if not self.solved and normalized_moves:
            raise ValueError("Unsolved results must not include a solution move sequence.")

        object.__setattr__(self, "moves", normalized_moves)
        object.__setattr__(self, "state_path", normalized_path)


class ExpandedCounter:
    """Small counter implementing the documented expanded-state convention."""

    def __init__(self) -> None:
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def record_successor_generation(self) -> None:
        # ASSIGNMENT REQUIREMENT R19 — EXPANDED STATES
        # A search algorithm should call this only after a state has been popped
        # from the frontier and the algorithm is about to generate or examine
        # successors. A popped goal is checked before this call and is therefore
        # not counted as expanded.
        self._count += 1


def reconstruct_path(
    start_state: PuzzleState,
    goal_state: PuzzleState,
    predecessors: Mapping[PuzzleState, SearchStep],
) -> tuple[tuple[str, ...], tuple[PuzzleState, ...]]:
    """Return `(moves, states)` from `start_state` to `goal_state`.

    # ASSIGNMENT REQUIREMENT R17 — RETURNED MOVE SEQUENCE
    # The reconstructed move sequence preserves the documented blank-movement
    # names (`UP`, `DOWN`, `LEFT`, `RIGHT`) exactly as stored by search.
    """

    if start_state == goal_state:
        return (), (start_state,)

    moves: list[str] = []
    states: list[PuzzleState] = [goal_state]
    current = goal_state
    seen = {goal_state}

    while current != start_state:
        try:
            step = predecessors[current]
        except KeyError as exc:
            raise ValueError("Cannot reconstruct path: a predecessor link is missing.") from exc

        if step.previous_state is None or step.move is None:
            raise ValueError("Cannot reconstruct path: encountered an incomplete predecessor link.")
        if current != step.previous_state.apply_move(step.move):
            raise ValueError("Cannot reconstruct path: predecessor move does not reach the current state.")
        if step.previous_state in seen:
            raise ValueError("Cannot reconstruct path: predecessor links contain a cycle.")

        moves.append(step.move)
        current = step.previous_state
        states.append(current)
        seen.add(current)

    moves.reverse()
    states.reverse()
    return tuple(moves), tuple(states)


def make_solved_result(
    algorithm: str,
    start_state: PuzzleState,
    goal_state: PuzzleState,
    predecessors: Mapping[PuzzleState, SearchStep],
    expanded_states: int,
) -> SearchResult:
    """Create a solved `SearchResult` using shared path reconstruction."""

    moves, state_path = reconstruct_path(start_state, goal_state, predecessors)
    # ASSIGNMENT REQUIREMENT R18 — SOLUTION LENGTH
    # The solved result derives solution_length from the reconstructed sequence,
    # preserving solution_length == len(move_sequence), including zero at goal.
    return SearchResult(
        algorithm=algorithm,
        solved=True,
        moves=moves,
        solution_length=len(moves),
        expanded_states=expanded_states,
        status=STATUS_SOLVED,
        message="Solution found.",
        start_state=start_state,
        goal_state=goal_state,
        state_path=state_path,
    )


def make_invalid_result(algorithm: str, message: str) -> SearchResult:
    """Create a standardized result for malformed puzzle input."""

    return SearchResult(
        algorithm=algorithm,
        solved=False,
        status=STATUS_INVALID,
        message=message,
    )


def make_unsolvable_result(
    algorithm: str,
    start_state: PuzzleState,
    goal_state: PuzzleState,
    message: str = "Puzzle is structurally valid but unsolvable.",
) -> SearchResult:
    """Create a standardized result for valid but unsolvable puzzle input."""

    return SearchResult(
        algorithm=algorithm,
        solved=False,
        status=STATUS_UNSOLVABLE,
        message=message,
        start_state=start_state,
        goal_state=goal_state,
    )
