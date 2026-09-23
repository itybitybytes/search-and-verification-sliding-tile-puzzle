"""Fixed 3x3 verification boards for grader-facing solver evidence.

File purpose:
    Centralize transparent test boards that the future top-level verification
    script will use. Solvable non-goal boards are derived from legal blank moves
    from the lower-right blank goal, which guarantees reachability.

Assignment requirements supported:
    R20-R27: Future runnable verification script cases and comparison inputs.

Graded submission artifact:
    Supporting module used by future `03_verify_solver.py`.
"""

from __future__ import annotations

from .constants import DOWN, LEFT, RIGHT, UP

VERIFICATION_SIZE = 3

# Lower-right blank goal:
# 1 2 3
# 4 5 6
# 7 8 _
SOLVED_BOARD = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Exactly one blank move from the goal. Applying RIGHT solves it.
ONE_MOVE_SEQUENCE_FROM_GOAL = (LEFT,)
ONE_MOVE_BOARD = (1, 2, 3, 4, 5, 6, 7, 0, 8)
ONE_MOVE_BFS_MINIMUM_LENGTH = 1

# Several-move case derived by legal blank moves from the goal:
# LEFT, UP, LEFT
SEVERAL_MOVE_SEQUENCE_FROM_GOAL = (LEFT, UP, LEFT)
SEVERAL_MOVE_BOARD = (1, 2, 3, 0, 4, 6, 7, 5, 8)
SEVERAL_MOVE_BFS_MINIMUM_LENGTH = 3

# Unmistakably malformed board: tile 7 is duplicated and tile 8 is missing.
INVALID_BOARD = (1, 2, 3, 4, 5, 6, 7, 7, 0)

# Structurally valid 3x3 tile set with incorrect parity for the lower-right
# blank goal. Swapping 7 and 8 creates exactly one inversion, so it is unsolvable.
UNSOLVABLE_BOARD = (1, 2, 3, 4, 5, 6, 8, 7, 0)

# Algorithm-comparison case derived by legal blank moves from the goal:
# LEFT, UP, LEFT, DOWN, RIGHT, UP
COMPARISON_SEQUENCE_FROM_GOAL = (LEFT, UP, LEFT, DOWN, RIGHT, UP)
COMPARISON_BOARD = (1, 2, 3, 7, 0, 6, 5, 4, 8)
COMPARISON_BFS_MINIMUM_LENGTH = 6

VERIFICATION_CASES = {
    "solved": SOLVED_BOARD,
    "one_move": ONE_MOVE_BOARD,
    "several_moves": SEVERAL_MOVE_BOARD,
    "invalid": INVALID_BOARD,
    "unsolvable": UNSOLVABLE_BOARD,
    "comparison": COMPARISON_BOARD,
}
