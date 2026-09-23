"""Direct runnable verification for the text-only Python solver.

Run from this directory with:

    python 03_verify_solver.py

This required graded artifact addresses R20-R29 by printing real algorithm
results and asserting the required correctness properties.

Reviewer anchors:

- R20 runnable verification file.
- R21 solved state tested.
- R22 one-move state tested.
- R23 several-move state tested.
- R24 invalid and unsolvable states tested.
- R25 BFS, A* misplaced, and A* Manhattan compared.
- R26 solution length reported for all three algorithms.
- R27 expanded states reported for all three algorithms.
- R28 Python solver artifact exercised through `02_python_solver.py`.
- R29 verification script artifact exists and runs directly.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _load_solver() -> ModuleType:
    """Load `02_python_solver.py`, whose leading digit prevents normal import."""

    solver_path = Path(__file__).with_name("02_python_solver.py")
    spec = importlib.util.spec_from_file_location("python_solver_facade", solver_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load solver facade from {solver_path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


solver = _load_solver()


def section(title: str) -> None:
    print()
    print("============================================================")
    print(title)
    print("=" * len(title))


def render_board(board: tuple[int, ...]) -> str:
    return solver.format_board(board, 3)


def verify_solution_reaches_goal(board: tuple[int, ...], moves: tuple[str, ...]) -> None:
    """Assert that every returned move is legal and reaches the goal."""

    state = solver.PuzzleState(board, 3)
    for move in moves:
        assert move in state.legal_moves(), f"Illegal move {move!r} from {state.board}"
        state = state.apply_move(move)
    assert state.is_goal(), f"Move sequence did not reach goal; ended at {state.board}"


def assert_solved_result(board: tuple[int, ...], result: object) -> None:
    assert result.solved, f"{result.algorithm} did not solve the board: {result.message}"
    assert result.solution_length == len(result.moves), (
        f"{result.algorithm} solution_length does not equal len(moves)."
    )
    verify_solution_reaches_goal(board, result.moves)


def print_successful_search(board: tuple[int, ...], result: object) -> None:
    print("Starting state:")
    print(render_board(board))
    print(f"Algorithm: {result.algorithm}")
    print(f"Solved: {result.solved}")
    print(f"Move sequence: {', '.join(result.moves) if result.moves else '(empty)'}")
    print(f"Solution length: {result.solution_length}")
    print(f"Expanded states: {result.expanded_states}")


def run_success_case(title: str, board: tuple[int, ...]) -> object:
    section(title)
    result = solver.breadth_first_search(board)
    print_successful_search(board, result)
    assert_solved_result(board, result)
    return result


def run_rejection_case(title: str, board: tuple[int, ...], expected_status: str) -> None:
    section(title)
    print("Starting state tuple:")
    print(board)
    for name, search in solver.ALGORITHMS:
        result = search(board)
        print(f"{name}: solved={result.solved}, status={result.status}, message={result.message}")
        assert not result.solved, f"{name} unexpectedly solved {title}."
        assert result.status == expected_status, (
            f"{name} expected status {expected_status!r}, got {result.status!r}."
        )


def run_comparison() -> None:
    section("BFS VS A* COMPARISON")
    board = solver.COMPARISON_STATE_3X3
    print("Starting state:")
    print(render_board(board))
    print(f"Constructed from legal blank moves: {', '.join(solver.COMPARISON_SETUP)}")
    print()

    results = []
    for name, search in solver.ALGORITHMS:
        result = search(board)
        assert_solved_result(board, result)
        results.append(result)
        print_successful_search(board, result)
        print()

    print("Algorithm | Solution Length | Expanded States")
    for result in results:
        print(f"{result.algorithm} | {result.solution_length} | {result.expanded_states}")

    lengths = {result.solution_length for result in results}
    assert len(lengths) == 1, f"Algorithms disagreed on solution length: {lengths}"


def main() -> None:
    # ASSIGNMENT REQUIREMENT R20 — RUNNABLE VERIFICATION FILE
    # This script is intentionally direct and noninteractive: python 03_verify_solver.py

    assert solver.misplaced_tiles(solver.SOLVED_STATE_3X3) == 0
    assert solver.manhattan_distance(solver.SOLVED_STATE_3X3) == 0

    solved = run_success_case("TEST 1 — SOLVED PUZZLE", solver.SOLVED_STATE_3X3)
    assert solved.solution_length == 0, "Solved puzzle should require zero moves."

    one_move = run_success_case("TEST 2 — ONE MOVE FROM GOAL", solver.ONE_MOVE_STATE_3X3)
    assert one_move.solution_length == 1, "One-move puzzle should require one move."

    several = run_success_case(
        "TEST 3 — SEVERAL MOVES FROM GOAL",
        solver.SEVERAL_MOVE_STATE_3X3,
    )
    assert several.solution_length > 1, "Several-move puzzle should require multiple moves."

    run_rejection_case(
        "TEST 4 — INVALID PUZZLE",
        solver.INVALID_STATE_3X3,
        "invalid",
    )
    run_rejection_case(
        "TEST 5 — UNSOLVABLE PUZZLE",
        solver.UNSOLVABLE_STATE_3X3,
        "unsolvable",
    )

    run_comparison()

    print()
    print("All verification assertions passed.")


if __name__ == "__main__":
    main()
