"""Search algorithms for the sliding-tile puzzle solver.

File purpose:
    Provide assignment-required search implementations while reusing the
    shared puzzle model, validation, solvability, and result infrastructure.

Assignment requirements addressed:
    R07: A* deterministic tie-breaking.
    R10: Breadth-first search.
    R11: BFS minimum-move guarantee for tested 3x3 states.
    R12: A* with misplaced-tiles heuristic.
    R13: A* with Manhattan-distance heuristic.
    R17: Returned move sequence can be inspected.
    R18: Solution length is tracked.
    R19: Expanded states are tracked using the documented definition.

Graded submission artifact:
    Supporting module used by the required root artifact `02_python_solver.py`.
"""

from __future__ import annotations

from collections import deque
from heapq import heappop, heappush
from itertools import count
from typing import Callable, Iterable

from .heuristics import manhattan_distance, misplaced_tiles
from .puzzle_state import PuzzleState
from .search_support import (
    STATUS_NOT_SOLVED,
    ExpandedCounter,
    SearchResult,
    SearchStep,
    make_invalid_result,
    make_solved_result,
    make_unsolvable_result,
)
from .solvability import is_solvable
from .validation import InvalidPuzzleStateError

BFS_ALGORITHM_NAME = "BFS"
ASTAR_MISPLACED_ALGORITHM_NAME = "A* Misplaced"
ASTAR_MANHATTAN_ALGORITHM_NAME = "A* Manhattan"


def _coerce_state(initial: PuzzleState | Iterable[int], size: int | None) -> PuzzleState:
    if isinstance(initial, PuzzleState):
        if size is not None and initial.size != size:
            raise InvalidPuzzleStateError("Supplied size does not match the PuzzleState dimension.")
        return initial
    return PuzzleState(tuple(initial), size)


def breadth_first_search(initial: PuzzleState | Iterable[int], size: int | None = None) -> SearchResult:
    """Solve a sliding-tile puzzle with breadth-first search.

    # ASSIGNMENT REQUIREMENT R10 — BREADTH-FIRST SEARCH
    # BFS validates the input, rejects unsolvable states before traversal, uses
    # a FIFO frontier, avoids revisiting discovered states, records predecessor
    # links, and returns the shared `SearchResult` structure.

    # ASSIGNMENT REQUIREMENT R11 — BFS MINIMUM-MOVE GUARANTEE
    # With unit-cost puzzle moves, FIFO breadth-first traversal explores all
    # depth-d states before any depth-(d+1) state, so the first goal reached is
    # a shortest-path solution for the tested 3x3 cases.
    """

    try:
        start_state = _coerce_state(initial, size)
    except (InvalidPuzzleStateError, ValueError, TypeError) as exc:
        return make_invalid_result(BFS_ALGORITHM_NAME, str(exc))

    goal_state = PuzzleState.goal(start_state.size)

    if not is_solvable(start_state.tiles, start_state.size):
        return make_unsolvable_result(BFS_ALGORITHM_NAME, start_state, goal_state)

    if start_state == goal_state:
        return make_solved_result(BFS_ALGORITHM_NAME, start_state, goal_state, {}, expanded_states=0)

    frontier: deque[PuzzleState] = deque([start_state])
    discovered = {start_state}
    predecessors: dict[PuzzleState, SearchStep] = {}
    expanded = ExpandedCounter()

    while frontier:
        current = frontier.popleft()

        if current == goal_state:
            return make_solved_result(
                BFS_ALGORITHM_NAME,
                start_state,
                goal_state,
                predecessors,
                expanded_states=expanded.count,
            )

        expanded.record_successor_generation()
        for move, next_state in current.successors():
            if next_state in discovered:
                continue
            discovered.add(next_state)
            predecessors[next_state] = SearchStep(previous_state=current, move=move)
            frontier.append(next_state)

    return SearchResult(
        algorithm=BFS_ALGORITHM_NAME,
        solved=False,
        status=STATUS_NOT_SOLVED,
        message="No solution found after exhausting the BFS frontier.",
        start_state=start_state,
        goal_state=goal_state,
        expanded_states=expanded.count,
    )


def _a_star_search(
    initial: PuzzleState | Iterable[int],
    size: int | None,
    algorithm_name: str,
    heuristic: Callable[[PuzzleState], int],
) -> SearchResult:
    try:
        start_state = _coerce_state(initial, size)
    except (InvalidPuzzleStateError, ValueError, TypeError) as exc:
        return make_invalid_result(algorithm_name, str(exc))

    goal_state = PuzzleState.goal(start_state.size)

    if not is_solvable(start_state.tiles, start_state.size):
        return make_unsolvable_result(algorithm_name, start_state, goal_state)

    insertion_order = count()
    start_h = heuristic(start_state)
    frontier: list[tuple[int, int, int, int, PuzzleState]] = []

    # ASSIGNMENT REQUIREMENT R07 — A* TIE-BREAKING
    # Heap entries are ordered by lowest f = g + h, then lowest h, then earliest
    # insertion order. The counter also prevents Python from comparing
    # PuzzleState objects directly when priorities tie.
    heappush(frontier, (start_h, start_h, next(insertion_order), 0, start_state))

    best_g = {start_state: 0}
    predecessors: dict[PuzzleState, SearchStep] = {}
    expanded = ExpandedCounter()

    while frontier:
        _, _, _, current_g, current = heappop(frontier)

        if current_g != best_g.get(current):
            continue

        if current == goal_state:
            return make_solved_result(
                algorithm_name,
                start_state,
                goal_state,
                predecessors,
                expanded_states=expanded.count,
            )

        expanded.record_successor_generation()
        for move, next_state in current.successors():
            next_g = current_g + 1
            if next_g >= best_g.get(next_state, float("inf")):
                continue

            best_g[next_state] = next_g
            predecessors[next_state] = SearchStep(previous_state=current, move=move)
            next_h = heuristic(next_state)
            next_f = next_g + next_h
            heappush(frontier, (next_f, next_h, next(insertion_order), next_g, next_state))

    return SearchResult(
        algorithm=algorithm_name,
        solved=False,
        status=STATUS_NOT_SOLVED,
        message="No solution found after exhausting the A* frontier.",
        start_state=start_state,
        goal_state=goal_state,
        expanded_states=expanded.count,
    )


def a_star_misplaced(initial: PuzzleState | Iterable[int], size: int | None = None) -> SearchResult:
    """Solve a puzzle with A* using the misplaced-tiles heuristic."""

    # ASSIGNMENT REQUIREMENT R12 — A* MISPLACED TILES
    # This public entry point selects f = g + misplaced_tiles(state) while the
    # shared A* engine handles validation, priority ordering, predecessor
    # tracking, path reconstruction, and expanded-state reporting.
    return _a_star_search(initial, size, ASTAR_MISPLACED_ALGORITHM_NAME, misplaced_tiles)


def a_star_manhattan(initial: PuzzleState | Iterable[int], size: int | None = None) -> SearchResult:
    """Solve a puzzle with A* using the Manhattan-distance heuristic."""

    # ASSIGNMENT REQUIREMENT R13 — A* MANHATTAN DISTANCE
    # This public entry point selects f = g + manhattan_distance(state) while
    # reusing the same A* machinery and result structure as the misplaced
    # heuristic configuration.
    return _a_star_search(initial, size, ASTAR_MANHATTAN_ALGORITHM_NAME, manhattan_distance)
