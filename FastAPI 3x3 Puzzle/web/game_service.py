"""Backend game and solver-demo services for the web application.

File purpose:
    Keep browser game concerns separate from the graded Python solver modules.

Architecture decision:
    GAME MODE supports manual play for 3x3, 4x4, and 5x5 boards.
    ASSIGNMENT SOLVER MODE exposes only fixed reasonable 3x3 solver examples.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable

from solver import (
    ASTAR_MANHATTAN_ALGORITHM_NAME,
    ASTAR_MISPLACED_ALGORITHM_NAME,
    BFS_ALGORITHM_NAME,
    COMPARISON_BOARD,
    DOWN,
    LEFT,
    RIGHT,
    SEVERAL_MOVE_BOARD,
    SOLVED_BOARD,
    UP,
    VERIFICATION_SIZE,
    PuzzleState,
    SearchResult,
    a_star_manhattan,
    a_star_misplaced,
    breadth_first_search,
    is_solvable,
)


@dataclass(frozen=True)
class Difficulty:
    key: str
    label: str
    size: int
    scramble_moves: int


DIFFICULTIES: dict[str, Difficulty] = {
    "easy": Difficulty("easy", "Easy", 3, 24),
    "medium": Difficulty("medium", "Medium", 4, 60),
    "hard": Difficulty("hard", "Hard", 5, 100),
}

INVERSE_MOVES = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

SOLVER_DEMO_CASES = {
    "solved": SOLVED_BOARD,
    "several": SEVERAL_MOVE_BOARD,
    "comparison": COMPARISON_BOARD,
}


def difficulty_payload() -> list[dict[str, int | str]]:
    return [
        {
            "key": difficulty.key,
            "label": difficulty.label,
            "size": difficulty.size,
            "dimensions": f"{difficulty.size} x {difficulty.size}",
        }
        for difficulty in DIFFICULTIES.values()
    ]


def state_payload(state: PuzzleState) -> dict[str, object]:
    return {
        "size": state.size,
        "tiles": list(state.tiles),
        "blank": state.blank_index(),
        "is_goal": state.is_goal(),
        "solvable": is_solvable(state.tiles, state.size),
    }


def generate_playable_puzzle(difficulty_key: str, seed: int | None = None) -> dict[str, object]:
    """Generate a GAME MODE puzzle by legal scrambling from the goal."""

    if difficulty_key not in DIFFICULTIES:
        supported = ", ".join(DIFFICULTIES)
        raise ValueError(f"Unsupported difficulty {difficulty_key!r}. Choose one of: {supported}.")

    difficulty = DIFFICULTIES[difficulty_key]
    rng = random.Random(seed)
    state = PuzzleState.goal(difficulty.size)
    previous_move: str | None = None
    scramble_sequence: list[str] = []

    for _ in range(difficulty.scramble_moves):
        legal_moves = list(state.legal_moves())
        if previous_move is not None and len(legal_moves) > 1:
            reverse = INVERSE_MOVES[previous_move]
            legal_moves = [move for move in legal_moves if move != reverse]

        move = rng.choice(legal_moves)
        state = state.apply_move(move)
        previous_move = move
        scramble_sequence.append(move)

    if state.is_goal():
        move = rng.choice(list(state.legal_moves()))
        state = state.apply_move(move)
        scramble_sequence.append(move)

    return {
        "mode": "GAME MODE",
        "difficulty": difficulty.label,
        "difficulty_key": difficulty.key,
        "dimensions": f"{difficulty.size} x {difficulty.size}",
        "state": state_payload(state),
        "scramble_moves": len(scramble_sequence),
    }


def _result_payload(result: SearchResult) -> dict[str, object]:
    return {
        "algorithm": result.algorithm,
        "solved": result.solved,
        "status": result.status,
        "message": result.message,
        "moves": list(result.moves),
        "solution_length": result.solution_length,
        "expanded_states": result.expanded_states,
    }


def solver_demo(case: str = "comparison") -> dict[str, object]:
    """Run ASSIGNMENT SOLVER MODE on a fixed reasonable 3x3 case only."""

    if case not in SOLVER_DEMO_CASES:
        supported = ", ".join(SOLVER_DEMO_CASES)
        raise ValueError(f"Unsupported solver demo case {case!r}. Choose one of: {supported}.")

    board = SOLVER_DEMO_CASES[case]
    algorithms: tuple[tuple[str, Callable[[tuple[int, ...], int | None], SearchResult]], ...] = (
        (BFS_ALGORITHM_NAME, breadth_first_search),
        (ASTAR_MISPLACED_ALGORITHM_NAME, a_star_misplaced),
        (ASTAR_MANHATTAN_ALGORITHM_NAME, a_star_manhattan),
    )

    return {
        "mode": "ASSIGNMENT SOLVER MODE",
        "note": "Solver demonstrations are intentionally limited to fixed reasonable 3x3 cases.",
        "case": case,
        "state": state_payload(PuzzleState(board, VERIFICATION_SIZE)),
        "results": [_result_payload(search(board, VERIFICATION_SIZE)) for _, search in algorithms],
    }
