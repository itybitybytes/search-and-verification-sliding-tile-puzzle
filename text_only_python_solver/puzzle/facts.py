"""Did You Know fact rotation for the text-only support systems.

File purpose:
    Store concise puzzle/search facts and select the active fact from elapsed
    time without using a background thread.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver subproject.
"""

from __future__ import annotations

from math import floor
from typing import Sequence

FACT_ROTATION_SECONDS = 30

FACTS: tuple[str, ...] = (
    "Sliding puzzles model a state space where each board is a node.",
    "Breadth-first search explores all states at one move before trying two moves.",
    "A* combines path cost so far with a heuristic estimate to prioritize states.",
    "Manhattan distance adds each tile's row and column distance from its goal.",
    "The misplaced-tiles heuristic counts numbered tiles outside their goal spots.",
    "Admissible heuristics never overestimate the remaining cost to the goal.",
    "The blank tile is ignored by both required heuristic functions.",
    "Optimal search returns a shortest solution when its assumptions are satisfied.",
)


def fact_index_for_elapsed(
    elapsed_seconds: int,
    facts: Sequence[str] = FACTS,
    rotation_seconds: int = FACT_ROTATION_SECONDS,
) -> int:
    """Return the deterministic fact index for an elapsed-time value."""

    if not facts:
        raise ValueError("At least one fact is required.")
    if rotation_seconds <= 0:
        raise ValueError("rotation_seconds must be positive.")
    if elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be nonnegative.")
    return floor(elapsed_seconds / rotation_seconds) % len(facts)


def current_fact(
    elapsed_seconds: int,
    facts: Sequence[str] = FACTS,
    rotation_seconds: int = FACT_ROTATION_SECONDS,
) -> str:
    """Return the current fact without starting timers or background threads."""

    return facts[fact_index_for_elapsed(elapsed_seconds, facts, rotation_seconds)]
