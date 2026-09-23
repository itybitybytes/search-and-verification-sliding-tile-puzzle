"""Solvable puzzle generation for the text-only support systems.

File purpose:
    Create playable 3x3, 4x4, and 5x5 puzzle boards by legal scrambling from
    the documented lower-right blank goal state.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver subproject.
"""

from __future__ import annotations

import random
from typing import Mapping

from .model import PuzzleState
from .validation import SUPPORTED_SIZES, is_solvable, validate_board

DIFFICULTY_SIZES: Mapping[str, int] = {
    "Easy": 3,
    "Medium": 4,
    "Hard": 5,
}

DEFAULT_SCRAMBLE_STEPS: Mapping[int, int] = {
    3: 30,
    4: 80,
    5: 150,
}

REVERSE_MOVE = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


def board_size_for_difficulty(difficulty: str) -> int:
    """Return the supported board size for Easy, Medium, or Hard."""

    try:
        return DIFFICULTY_SIZES[difficulty]
    except KeyError as exc:
        expected = ", ".join(DIFFICULTY_SIZES)
        raise ValueError(f"Unknown difficulty {difficulty!r}; expected one of {expected}.") from exc


def difficulty_for_board_size(board_size: int) -> str:
    """Return the display difficulty for a supported board size."""

    for difficulty, size in DIFFICULTY_SIZES.items():
        if size == board_size:
            return difficulty
    raise ValueError(f"Board size {board_size} is unsupported.")


def generate_puzzle_by_size(
    board_size: int,
    scramble_steps: int | None = None,
    rng: random.Random | None = None,
) -> PuzzleState:
    """Generate a valid solvable non-goal board by applying legal blank moves.

    The generator never randomly permutes all tiles. It starts at the goal and
    walks through legal puzzle states, so the returned board is solvable by
    construction. Immediate reversal of the previous shuffle move is avoided
    when another legal move is available.
    """

    if board_size not in SUPPORTED_SIZES:
        raise ValueError("Board size must be one of 3, 4, or 5.")

    if scramble_steps is None:
        scramble_steps = DEFAULT_SCRAMBLE_STEPS[board_size]
    if scramble_steps < 1:
        raise ValueError("scramble_steps must be at least 1 so the board is not still goal.")

    random_source = rng if rng is not None else random.Random()
    state = PuzzleState.goal(board_size)
    previous_move: str | None = None

    for _ in range(scramble_steps):
        legal_moves = list(state.legal_moves())
        if previous_move is not None and len(legal_moves) > 1:
            reverse = REVERSE_MOVE[previous_move]
            legal_moves = [move for move in legal_moves if move != reverse]
        move = random_source.choice(legal_moves)
        state = state.apply_move(move)
        previous_move = move

    if state.is_goal():
        legal_moves = list(state.legal_moves())
        state = state.apply_move(random_source.choice(legal_moves))

    validate_board(state.board, board_size)
    if not is_solvable(state.board, board_size):
        raise RuntimeError("Generated puzzle should be solvable by legal scrambling.")
    return state


def generate_puzzle(
    difficulty: str,
    scramble_steps: int | None = None,
    rng: random.Random | None = None,
) -> PuzzleState:
    """Generate an Easy 3x3, Medium 4x4, or Hard 5x5 puzzle."""

    return generate_puzzle_by_size(
        board_size_for_difficulty(difficulty),
        scramble_steps=scramble_steps,
        rng=rng,
    )
