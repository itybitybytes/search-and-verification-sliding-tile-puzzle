"""Core puzzle model package for the text-only sliding-tile solver."""

from .facts import FACT_ROTATION_SECONDS, FACTS, current_fact, fact_index_for_elapsed
from .generator import (
    DEFAULT_SCRAMBLE_STEPS,
    DIFFICULTY_SIZES,
    REVERSE_MOVE,
    board_size_for_difficulty,
    difficulty_for_board_size,
    generate_puzzle,
    generate_puzzle_by_size,
)
from .heuristics import manhattan_distance, misplaced_tiles
from .model import BLANK, MOVES, SUPPORTED_SIZES, PuzzleState, goal_board
from .records import (
    DEFAULT_RECORDS_PATH,
    append_record,
    format_elapsed_time,
    load_records,
    records_for_username,
    save_records,
    validate_completion_record,
)
from .results import (
    SearchResult,
    invalid_result,
    reconstruct_moves,
    solved_result,
    unsolvable_result,
)
from .search import (
    A_STAR_MANHATTAN_ALGORITHM_NAME,
    A_STAR_MISPLACED_ALGORITHM_NAME,
    BFS_ALGORITHM_NAME,
    a_star_manhattan,
    a_star_misplaced,
    breadth_first_search,
)
from .validation import (
    InvalidPuzzleStateError,
    blank_row_from_bottom,
    count_inversions,
    infer_dimension,
    is_solvable,
    validate_board,
)

__all__ = [
    "BLANK",
    "DEFAULT_SCRAMBLE_STEPS",
    "DEFAULT_RECORDS_PATH",
    "DIFFICULTY_SIZES",
    "FACTS",
    "FACT_ROTATION_SECONDS",
    "MOVES",
    "REVERSE_MOVE",
    "SUPPORTED_SIZES",
    "PuzzleState",
    "append_record",
    "board_size_for_difficulty",
    "current_fact",
    "difficulty_for_board_size",
    "fact_index_for_elapsed",
    "format_elapsed_time",
    "generate_puzzle",
    "generate_puzzle_by_size",
    "goal_board",
    "load_records",
    "manhattan_distance",
    "misplaced_tiles",
    "records_for_username",
    "save_records",
    "validate_completion_record",
    "SearchResult",
    "invalid_result",
    "reconstruct_moves",
    "solved_result",
    "unsolvable_result",
    "A_STAR_MANHATTAN_ALGORITHM_NAME",
    "A_STAR_MISPLACED_ALGORITHM_NAME",
    "BFS_ALGORITHM_NAME",
    "a_star_manhattan",
    "a_star_misplaced",
    "breadth_first_search",
    "InvalidPuzzleStateError",
    "blank_row_from_bottom",
    "count_inversions",
    "infer_dimension",
    "is_solvable",
    "validate_board",
]
