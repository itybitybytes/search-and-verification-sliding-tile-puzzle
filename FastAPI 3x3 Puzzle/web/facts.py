"""Maintainable fact content for the left-sidebar Did You Know panel."""

from __future__ import annotations


SIDEBAR_FACTS: tuple[str, ...] = (
    "The classic 8-puzzle has 181,440 reachable arrangements.",
    "A single swap of two numbered tiles changes puzzle parity.",
    "Breadth-first search checks all one-move states before any two-move states.",
    "A* combines moves already made with an estimate of moves still needed.",
    "Manhattan distance adds each tile's row and column distance from goal.",
    "A heuristic is useful when it points search toward promising states.",
    "The blank is stored as 0 even when the browser decorates it.",
    "Sliding puzzles are state-space problems: each board is one state.",
    "Avoiding repeated states keeps search from walking in circles.",
    "An admissible heuristic never overestimates the remaining cost.",
    "The lower-right blank goal makes the solved state easy to inspect.",
    "Legal moves are orthogonal only: up, down, left, or right.",
)
