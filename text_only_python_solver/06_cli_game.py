"""Portable terminal game for the text-only sliding-tile puzzle.

Run from this directory with:

    python 06_cli_game.py

The CLI intentionally reuses the generalized puzzle engine rather than
duplicating game loops for 3x3, 4x4, and 5x5 boards.
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable

from puzzle import (
    DIFFICULTY_SIZES,
    MOVES,
    PuzzleState,
    SearchResult,
    a_star_manhattan,
    a_star_misplaced,
    append_record,
    breadth_first_search,
    current_fact,
    format_elapsed_time,
    generate_puzzle,
    goal_board,
    records_for_username,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DIFFICULTY_MENU = {
    "1": "Easy",
    "EASY": "Easy",
    "2": "Medium",
    "MEDIUM": "Medium",
    "3": "Hard",
    "HARD": "Hard",
}

COMPARISON_SETUP = ("LEFT", "UP", "LEFT", "DOWN", "RIGHT", "UP")

ALGORITHMS = (
    ("BFS", breadth_first_search),
    ("A* Misplaced", a_star_misplaced),
    ("A* Manhattan", a_star_manhattan),
)

SOLVER_MENU = {
    "1": ("BFS", breadth_first_search),
    "BFS": ("BFS", breadth_first_search),
    "2": ("A* Misplaced", a_star_misplaced),
    "MISPLACED": ("A* Misplaced", a_star_misplaced),
    "A* MISPLACED": ("A* Misplaced", a_star_misplaced),
    "3": ("A* Manhattan", a_star_manhattan),
    "MANHATTAN": ("A* Manhattan", a_star_manhattan),
    "A* MANHATTAN": ("A* Manhattan", a_star_manhattan),
}

SearchFunction = Callable[[tuple[int, ...]], SearchResult]


def supports_unicode() -> bool:
    """Return whether the terminal should receive Unicode celebratory output."""

    if os.environ.get("PUZZLE_ASCII", "").strip() == "1":
        return False
    encoding = (sys.stdout.encoding or "").lower()
    return "utf" in encoding


def display_dash() -> str:
    return "—" if supports_unicode() else "-"


def title() -> None:
    print("============================================================")
    print("TEXT-ONLY SLIDING-TILE PUZZLE")
    print("============================================================")


def normalize_command(raw_value: str) -> str:
    return raw_value.strip().upper()


def pause(message: str = "Press Enter to continue...") -> None:
    input(message)


def ask_username() -> str:
    while True:
        username = input("USERNAME: ").strip()
        if username:
            return username
        print("Please enter a nonempty username, or press Ctrl+C to exit.")


def main_menu(username: str) -> None:
    while True:
        print()
        title()
        print(f"USERNAME: {username}")
        print()
        print("1. PLAY PUZZLE")
        print("2. SOLVER DEMONSTRATION")
        print("3. VIEW MY COMPLETION RECORDS")
        print("4. HELP")
        print("5. QUIT")
        choice = normalize_command(input("> "))

        if choice == "1" or choice == "PLAY" or choice == "PLAY PUZZLE":
            difficulty = choose_difficulty()
            if difficulty is not None:
                play_puzzle(username, difficulty)
        elif choice == "2" or choice == "SOLVER" or choice == "SOLVER DEMONSTRATION":
            solver_demonstration()
        elif choice == "3" or choice == "RECORDS" or choice == "VIEW":
            show_completion_records(username)
        elif choice == "4" or choice == "HELP":
            show_help()
        elif choice == "5" or choice == "QUIT" or choice == "Q":
            print("Goodbye.")
            return
        else:
            print("Unknown menu option. Choose 1, 2, 3, 4, or 5.")


def choose_difficulty() -> str | None:
    while True:
        print()
        print("DIFFICULTY")
        dash = display_dash()
        print(f"1. EASY   {dash} 3x3")
        print(f"2. MEDIUM {dash} 4x4")
        print(f"3. HARD   {dash} 5x5")
        print("Type QUIT to return to the main menu.")
        choice = normalize_command(input("> "))
        if choice in DIFFICULTY_MENU:
            return DIFFICULTY_MENU[choice]
        if choice in {"QUIT", "Q", "BACK"}:
            return None
        print("Unknown difficulty. Choose 1, 2, 3, or QUIT.")


def render_game_screen(
    username: str,
    difficulty: str,
    state: PuzzleState,
    moves: int,
    elapsed_seconds: int,
    message: str = "",
) -> None:
    print()
    print("============================================================")
    print("PUZZLE GAME")
    print("============================================================")
    print(f"USERNAME: {username}")
    print(f"DIFFICULTY: {difficulty.upper()} {display_dash()} {state.dimension}x{state.dimension}")
    print(f"MOVES: {moves}")
    print(f"TIME: {format_elapsed_time(elapsed_seconds)}")
    print()
    print("DID YOU KNOW?")
    print(current_fact(elapsed_seconds))
    print()
    print("PUZZLE BOARD")
    print(state.render(use_unicode_blank=supports_unicode()))
    print()
    if message:
        print(message)
    print("Commands: UP, DOWN, LEFT, RIGHT, HELP, NEW, QUIT")
    print("Directions describe movement of the BLANK.")


def play_puzzle(username: str, difficulty: str) -> None:
    """Run one generalized play loop for Easy, Medium, and Hard puzzles."""

    board_size = DIFFICULTY_SIZES[difficulty]
    state = generate_puzzle(difficulty)
    moves = 0
    start_time = time.monotonic()
    message = ""

    while True:
        elapsed_seconds = int(time.monotonic() - start_time)
        render_game_screen(username, difficulty, state, moves, elapsed_seconds, message)
        message = ""
        command = normalize_command(input("> "))

        if command in MOVES:
            if command not in state.legal_moves():
                # Terminal equivalent of shake + red + buzz: reject, bell, explain.
                print("\a", end="")
                message = f"[INVALID MOVE] The blank cannot move {command} from this position."
                continue

            state = state.apply_move(command)
            moves += 1

            if state.is_goal():
                final_seconds = int(time.monotonic() - start_time)
                render_game_screen(username, difficulty, state, moves, final_seconds)
                save_completion(username, difficulty, board_size, moves, final_seconds)
                pause()
                return
        elif command == "HELP":
            print()
            print("Move the blank with UP, DOWN, LEFT, or RIGHT.")
            print("A valid move swaps the blank with the adjacent numbered tile.")
            print("NEW starts a fresh puzzle at the same difficulty.")
            print("QUIT returns to the main menu.")
            pause()
        elif command == "NEW":
            state = generate_puzzle(difficulty)
            moves = 0
            start_time = time.monotonic()
            message = "[NEW PUZZLE] Generated a fresh solvable board."
        elif command in {"QUIT", "Q"}:
            print("Returning to main menu.")
            return
        elif command == "":
            message = "[UNKNOWN INPUT] Enter UP, DOWN, LEFT, RIGHT, HELP, NEW, or QUIT."
        else:
            message = f"[UNKNOWN INPUT] {command!r} is not a recognized command."


def save_completion(
    username: str,
    difficulty: str,
    board_size: int,
    moves: int,
    elapsed_seconds: int,
) -> None:
    celebration = "🎉" if supports_unicode() else "***"
    print("\a", end="")
    print()
    print("============================================================")
    print(f"{celebration} PUZZLE COMPLETE {celebration}")
    print("============================================================")
    print(f"Final moves: {moves}")
    print(f"Final time: {format_elapsed_time(elapsed_seconds)}")

    try:
        record = append_record(
            username=username,
            difficulty=difficulty,
            board_size=board_size,
            moves=moves,
            elapsed_seconds=elapsed_seconds,
        )
    except ValueError as exc:
        print(f"[RECORD ERROR] Completion was not saved: {exc}")
        return

    print(f"Saved completion record at {record['completed_at']}.")


def comparison_state_3x3() -> tuple[int, ...]:
    state = PuzzleState(goal_board(3), 3)
    for move in COMPARISON_SETUP:
        state = state.apply_move(move)
    return state.board


def solver_demonstration() -> None:
    board = comparison_state_3x3()
    while True:
        print()
        print("============================================================")
        print("SOLVER DEMONSTRATION")
        print("============================================================")
        print("Manual game: 3x3, 4x4, 5x5")
        print("Graded solver demonstration: reasonable 3x3 states")
        print("No arbitrary 4x4/5x5 BFS solving is exposed here.")
        print()
        print("Fixed 3x3 start state:")
        print(PuzzleState(board, 3).render(use_unicode_blank=supports_unicode()))
        print()
        print("1. BFS")
        print(f"2. A* {display_dash()} MISPLACED TILES")
        print(f"3. A* {display_dash()} MANHATTAN DISTANCE")
        print("4. COMPARE ALL THREE")
        print("5. RETURN")
        choice = normalize_command(input("> "))

        if choice in SOLVER_MENU:
            _name, search = SOLVER_MENU[choice]
            result = search(board)
            show_solver_result(board, result)
            maybe_step_through_solution(board, result)
            pause()
        elif choice == "4" or choice == "COMPARE" or choice == "COMPARE ALL THREE":
            compare_solver_algorithms(board)
            pause()
        elif choice in {"5", "RETURN", "QUIT", "Q", "BACK"}:
            return
        elif choice == "HELP":
            print("Choose one algorithm, compare all three, or return to the main menu.")
        else:
            print("Unknown solver option. Choose 1, 2, 3, 4, or 5.")


def show_solver_result(board: tuple[int, ...], result: SearchResult) -> None:
    print()
    print("------------------------------------------------------------")
    print("START STATE")
    print(PuzzleState(board, 3).render(use_unicode_blank=supports_unicode()))
    print()
    print(f"ALGORITHM: {result.algorithm}")
    print("UP/DOWN/LEFT/RIGHT describe movement of the blank.")
    print(f"MOVE SEQUENCE: {', '.join(result.moves) if result.moves else '(empty)'}")
    print(f"SOLUTION LENGTH: {result.solution_length}")
    print(f"EXPANDED STATES: {result.expanded_states}")
    print(f"STATUS: {result.status}")
    if result.message:
        print(f"MESSAGE: {result.message}")


def maybe_step_through_solution(board: tuple[int, ...], result: SearchResult) -> None:
    if not result.solved or not result.moves:
        return

    choice = normalize_command(input("Step through this move sequence? Y/N > "))
    if choice not in {"Y", "YES"}:
        return

    state = PuzzleState(board, 3)
    total_steps = len(result.moves)
    print()
    print("STEP 0 OF " + str(total_steps))
    print(state.render(use_unicode_blank=supports_unicode()))

    for index, move in enumerate(result.moves, start=1):
        input(f"Press Enter to apply {move}...")
        state = state.apply_move(move)
        print()
        print(f"STEP {index} OF {total_steps}")
        print(f"Applied blank move: {move}")
        print(state.render(use_unicode_blank=supports_unicode()))

    print("Reached goal." if state.is_goal() else "Playback ended before goal.")


def compare_solver_algorithms(board: tuple[int, ...]) -> None:
    print()
    print("------------------------------------------------------------")
    print("START STATE")
    print(PuzzleState(board, 3).render(use_unicode_blank=supports_unicode()))
    print()
    print("UP/DOWN/LEFT/RIGHT describe movement of the blank.")
    print()
    print("## Algorithm          Solution Length     Expanded States")
    results = []
    for _name, search in ALGORITHMS:
        result = search(board)
        results.append(result)
        print(f"{result.algorithm:<20} {result.solution_length:<19} {result.expanded_states}")

    print()
    print("Complete move sequences:")
    for result in results:
        sequence = ", ".join(result.moves) if result.moves else "(empty)"
        print(f"{result.algorithm}: {sequence}")


def show_completion_records(username: str) -> None:
    print()
    print("============================================================")
    print("MY COMPLETION RECORDS")
    print("============================================================")
    print(f"USERNAME: {username}")
    print()

    records = records_for_username(username)
    if not records:
        print("No completion records found yet.")
        pause()
        return

    print("Completed At | Difficulty | Size | Moves | Time")
    print("------------------------------------------------------------")
    for record in records:
        print(
            f"{record['completed_at']} | "
            f"{record['difficulty']} | "
            f"{record['board_size']}x{record['board_size']} | "
            f"{record['moves']} | "
            f"{record['formatted_time']}"
        )
    pause()


def show_help() -> None:
    print()
    print("============================================================")
    print("HELP")
    print("============================================================")
    print("PLAY PUZZLE generates a guaranteed-solvable board by legal moves from goal.")
    print("Easy is 3x3, Medium is 4x4, and Hard is 5x5.")
    print("During play, type UP, DOWN, LEFT, or RIGHT to move the blank.")
    print("Invalid moves leave the board and move count unchanged.")
    print("The timer starts when the puzzle begins, not during menus.")
    print("Solved games are saved to local JSON completion records.")
    pause()


def main() -> None:
    title()
    username = ask_username()
    main_menu(username)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Goodbye.")
