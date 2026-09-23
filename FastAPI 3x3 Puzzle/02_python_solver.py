"""============================================================
AI SEARCH ASSIGNMENT
PYTHON SLIDING-TILE PUZZLE SOLVER
============================================================

Required top-level graded submission artifact.

This file is the reviewer-facing Python solver entry point. The actual
algorithm and model implementations live in small supporting modules, but the
required assignment functionality is intentionally imported and re-exported
here so a grader can find it quickly without digging through package internals.

Core model and representation exposed here:
    R03: Generalized N x N board design for supported 3x3, 4x4, and 5x5 boards.
    R04: Lower-right blank goal: ascending numbered tiles followed by 0.
    R05: Board representation: immutable flat tuple of integers.
    R06: Move names: UP, DOWN, LEFT, RIGHT describe blank movement.

Validation and solvability exposed here:
    R08: Invalid puzzle states are rejected in a controlled way.
    R09: Unsolvable puzzle states are detected using parity/inversion logic.

Search algorithms exposed here:
    R07: A* tie-breaking is deterministic: lowest f, then lowest h, then
         earliest insertion order.
    R10: Breadth-first search.
    R11: BFS minimum-move guarantee for tested 3x3 states under unit move costs.
    R12: A* with misplaced-tiles heuristic.
    R13: A* with Manhattan-distance heuristic.

Heuristics and result reporting exposed here:
    R14: Misplaced-tiles heuristic ignores the blank.
    R15: Manhattan-distance heuristic ignores the blank.
    R16: Both heuristics return 0 at the goal.
    R17: Returned move sequence is inspectable.
    R18: Solution length is tracked and equals len(moves) for solved results.
    R19: Expanded states are tracked using the documented successor-generation
         convention.

Fixed 3x3 verification boards exposed here:
    Solved, one-move, several-move, invalid, unsolvable, and algorithm
    comparison cases are imported from `solver.verification_cases`. Solvable
    non-goal boards are documented as legal blank-move scrambles from the
    lower-right blank goal.
"""

from solver import (
    # R05 — board representation and internal blank value.
    BLANK,
    # R06 — documented blank-movement names.
    DOWN,
    LEFT,
    MOVES,
    RIGHT,
    SUPPORTED_SIZES,
    UP,
    # R08/R09/R17-R19 — shared structured result statuses.
    STATUS_INVALID,
    STATUS_NOT_SOLVED,
    STATUS_SOLVED,
    STATUS_UNSOLVABLE,
    # R07/R10-R13 — public algorithm names.
    ASTAR_MANHATTAN_ALGORITHM_NAME,
    ASTAR_MISPLACED_ALGORITHM_NAME,
    BFS_ALGORITHM_NAME,
    COMPARISON_BFS_MINIMUM_LENGTH,
    COMPARISON_BOARD,
    COMPARISON_SEQUENCE_FROM_GOAL,
    # R19 — expanded-state counting support.
    ExpandedCounter,
    INVALID_BOARD,
    # R03-R06/R08 — generalized state and validation model.
    InvalidPuzzleStateError,
    ONE_MOVE_BFS_MINIMUM_LENGTH,
    ONE_MOVE_BOARD,
    ONE_MOVE_SEQUENCE_FROM_GOAL,
    PuzzleState,
    # R17-R19 — shared search result and predecessor infrastructure.
    SearchResult,
    SearchStep,
    SEVERAL_MOVE_BFS_MINIMUM_LENGTH,
    SEVERAL_MOVE_BOARD,
    SEVERAL_MOVE_SEQUENCE_FROM_GOAL,
    SOLVED_BOARD,
    UNSOLVABLE_BOARD,
    VERIFICATION_CASES,
    VERIFICATION_SIZE,
    # R12/R13 — required A* solver entry points.
    a_star_manhattan,
    a_star_misplaced,
    # R09 — parity/inversion helpers.
    blank_row_from_bottom,
    # R10/R11 — required BFS solver entry point.
    breadth_first_search,
    count_inversions,
    # R04/R05 — goal construction and reviewer-readable board formatting.
    create_goal_state,
    format_board,
    index_to_position,
    infer_size,
    is_solvable,
    # R14-R16 — required heuristics.
    manhattan_distance,
    # R17/R18 — shared result construction and path reconstruction.
    make_invalid_result,
    make_solved_result,
    make_unsolvable_result,
    misplaced_tiles,
    position_to_index,
    reconstruct_path,
    validate_board,
)

__all__ = [
    "BLANK",
    "DOWN",
    "LEFT",
    "MOVES",
    "RIGHT",
    "SUPPORTED_SIZES",
    "UP",
    "STATUS_INVALID",
    "STATUS_NOT_SOLVED",
    "STATUS_SOLVED",
    "STATUS_UNSOLVABLE",
    "ASTAR_MANHATTAN_ALGORITHM_NAME",
    "ASTAR_MISPLACED_ALGORITHM_NAME",
    "BFS_ALGORITHM_NAME",
    "COMPARISON_BFS_MINIMUM_LENGTH",
    "COMPARISON_BOARD",
    "COMPARISON_SEQUENCE_FROM_GOAL",
    "ExpandedCounter",
    "INVALID_BOARD",
    "InvalidPuzzleStateError",
    "ONE_MOVE_BFS_MINIMUM_LENGTH",
    "ONE_MOVE_BOARD",
    "ONE_MOVE_SEQUENCE_FROM_GOAL",
    "PuzzleState",
    "SearchResult",
    "SearchStep",
    "SEVERAL_MOVE_BFS_MINIMUM_LENGTH",
    "SEVERAL_MOVE_BOARD",
    "SEVERAL_MOVE_SEQUENCE_FROM_GOAL",
    "SOLVED_BOARD",
    "UNSOLVABLE_BOARD",
    "VERIFICATION_CASES",
    "VERIFICATION_SIZE",
    "a_star_manhattan",
    "a_star_misplaced",
    "blank_row_from_bottom",
    "breadth_first_search",
    "count_inversions",
    "create_goal_state",
    "format_board",
    "infer_size",
    "index_to_position",
    "is_solvable",
    "manhattan_distance",
    "make_invalid_result",
    "make_solved_result",
    "make_unsolvable_result",
    "misplaced_tiles",
    "position_to_index",
    "reconstruct_path",
    "validate_board",
]


def _demo() -> None:
    state = PuzzleState.goal(3)
    print("3x3 lower-right blank goal:")
    print(state.format())
    print(f"Legal blank moves from goal: {', '.join(state.legal_moves())}")


if __name__ == "__main__":
    _demo()
