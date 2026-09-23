# 04 Test Evidence

This evidence file applies to the separate `text_only_python_solver/` subproject.

## Command Executed

```text
python 03_verify_solver.py
```

The results below are copied from the current implementation's real verification output. They are not estimated or hand-adjusted.

## Solver Conventions

Goal state:

```python
(1, 2, 3,
 4, 5, 6,
 7, 8, 0)
```

Board representation:

- Immutable flat `tuple[int, ...]`
- Row-major order
- Exactly `N*N` entries

Blank representation:

- Internal blank value is integer `0`.
- Terminal evidence renders the blank as `__`.
- The blank is excluded from tile numbering and heuristic values.

Move semantics:

- Move names are `UP`, `DOWN`, `LEFT`, and `RIGHT`.
- Directions describe movement of the blank, not movement of the numbered tile.

A* tie-breaking:

1. Lowest `f = g + h`
2. If `f` ties, lowest `h`
3. If both tie, earliest insertion order

Expanded-state definition:

- A state is expanded only when it is popped from the frontier and successors are generated or examined.
- A goal state recognized before successor generation is not counted as expanded.

## TEST 1 — SOLVED PUZZLE

Starting state:

```text
 1  2  3
 4  5  6
 7  8 __
```

Result:

- Algorithm: BFS
- Solved: True
- Move sequence: `(empty)`
- Solution length: `0`
- Expanded states: `0`

Correctness assertion result:

- Solved length equals `0`.
- Solution length equals `len(moves)`.
- Applying the returned move sequence reaches the goal.

## TEST 2 — ONE MOVE FROM GOAL

Starting state:

```text
 1  2  3
 4  5  6
 7 __  8
```

Result:

- Algorithm: BFS
- Solved: True
- Move sequence: `RIGHT`
- Solution length: `1`
- Expanded states: `1`

Correctness assertion result:

- One-move length equals `1`.
- Returned move is legal.
- Solution length equals `len(moves)`.
- Applying the returned move sequence reaches the goal.

## TEST 3 — SEVERAL MOVES FROM GOAL

Starting state:

```text
 1  2  3
__  4  6
 7  5  8
```

Result:

- Algorithm: BFS
- Solved: True
- Move sequence: `RIGHT, DOWN, RIGHT`
- Solution length: `3`
- Expanded states: `8`

Correctness assertion result:

- Several-move state requires more than one move.
- Returned moves are legal.
- Solution length equals `len(moves)`.
- Applying the returned move sequence reaches the goal.

## TEST 4 — INVALID PUZZLE

Starting state tuple:

```python
(1, 2, 3, 4, 5, 6, 7, 7, 0)
```

Result:

- BFS: `solved=False`, `status=invalid`, message: `Board contains duplicate tile value(s): [7].`
- A* Misplaced: `solved=False`, `status=invalid`, message: `Board contains duplicate tile value(s): [7].`
- A* Manhattan: `solved=False`, `status=invalid`, message: `Board contains duplicate tile value(s): [7].`

Correctness assertion result:

- Invalid state is handled without entering search.
- All three algorithms report `invalid`.

## TEST 5 — UNSOLVABLE PUZZLE

Starting state tuple:

```python
(1, 2, 3, 4, 5, 6, 8, 7, 0)
```

Result:

- BFS: `solved=False`, `status=unsolvable`, message: `Puzzle is structurally valid but unsolvable.`
- A* Misplaced: `solved=False`, `status=unsolvable`, message: `Puzzle is structurally valid but unsolvable.`
- A* Manhattan: `solved=False`, `status=unsolvable`, message: `Puzzle is structurally valid but unsolvable.`

Correctness assertion result:

- Valid but unsolvable state is detected by parity logic.
- All three algorithms report `unsolvable`.

## BFS VS A* COMPARISON

Starting state:

```text
 1  2  3
 7 __  6
 5  4  8
```

Constructed from legal blank moves:

```text
LEFT, UP, LEFT, DOWN, RIGHT, UP
```

Returned move sequence for all three algorithms:

```text
DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
```

| Algorithm | Solution Length | Expanded States |
|---|---:|---:|
| BFS | 6 | 48 |
| A* Misplaced | 6 | 8 |
| A* Manhattan | 6 | 6 |

Correctness assertion result:

- BFS found a solution.
- A* Misplaced found a solution.
- A* Manhattan found a solution.
- All three algorithms returned the same solution length: `6`.
- The returned move sequence is legal for each algorithm.
- Applying each returned move sequence reaches the goal.
- `misplaced_tiles(goal) == 0`.
- `manhattan_distance(goal) == 0`.

Measured expansion comparison:

- Manhattan expanded fewer states than A* Misplaced in this run.
- Manhattan expanded fewer states than BFS in this run.

## Complete Verification Output

```text
============================================================
TEST 1 — SOLVED PUZZLE
======================
Starting state:
 1  2  3
 4  5  6
 7  8 __
Algorithm: BFS
Solved: True
Move sequence: (empty)
Solution length: 0
Expanded states: 0

============================================================
TEST 2 — ONE MOVE FROM GOAL
===========================
Starting state:
 1  2  3
 4  5  6
 7 __  8
Algorithm: BFS
Solved: True
Move sequence: RIGHT
Solution length: 1
Expanded states: 1

============================================================
TEST 3 — SEVERAL MOVES FROM GOAL
================================
Starting state:
 1  2  3
__  4  6
 7  5  8
Algorithm: BFS
Solved: True
Move sequence: RIGHT, DOWN, RIGHT
Solution length: 3
Expanded states: 8

============================================================
TEST 4 — INVALID PUZZLE
=======================
Starting state tuple:
(1, 2, 3, 4, 5, 6, 7, 7, 0)
BFS: solved=False, status=invalid, message=Board contains duplicate tile value(s): [7].
A* Misplaced: solved=False, status=invalid, message=Board contains duplicate tile value(s): [7].
A* Manhattan: solved=False, status=invalid, message=Board contains duplicate tile value(s): [7].

============================================================
TEST 5 — UNSOLVABLE PUZZLE
==========================
Starting state tuple:
(1, 2, 3, 4, 5, 6, 8, 7, 0)
BFS: solved=False, status=unsolvable, message=Puzzle is structurally valid but unsolvable.
A* Misplaced: solved=False, status=unsolvable, message=Puzzle is structurally valid but unsolvable.
A* Manhattan: solved=False, status=unsolvable, message=Puzzle is structurally valid but unsolvable.

============================================================
BFS VS A* COMPARISON
====================
Starting state:
 1  2  3
 7 __  6
 5  4  8
Constructed from legal blank moves: LEFT, UP, LEFT, DOWN, RIGHT, UP

Starting state:
 1  2  3
 7 __  6
 5  4  8
Algorithm: BFS
Solved: True
Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
Solution length: 6
Expanded states: 48

Starting state:
 1  2  3
 7 __  6
 5  4  8
Algorithm: A* Misplaced
Solved: True
Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
Solution length: 6
Expanded states: 8

Starting state:
 1  2  3
 7 __  6
 5  4  8
Algorithm: A* Manhattan
Solved: True
Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
Solution length: 6
Expanded states: 6

Algorithm | Solution Length | Expanded States
BFS | 6 | 48
A* Misplaced | 6 | 8
A* Manhattan | 6 | 6

All verification assertions passed.
```

## Limitations

- Required solver evidence focuses on reasonable 3x3 states.
- This evidence does not claim that BFS is practical for arbitrary 4x4 or 5x5 puzzles.

## Latest Full Project Checks

Additional commands run after README finalization and CLI helper coverage:

```text
python 02_python_solver.py
python 03_verify_solver.py
python -m unittest discover -v
python 06_cli_game.py
```

Results:

- `python 02_python_solver.py` ran successfully.
- `python 03_verify_solver.py` ran successfully with the same measured solver metrics shown above.
- `python -m unittest discover -v` ran `58` tests in `0.104s` and reported `OK`.
- `python 06_cli_game.py` startup smoke test displayed the title, accepted username `tester`, displayed the main menu, and quit cleanly.
- CLI smoke testing also displayed the solver demonstration comparison table and generated playable Easy 3x3, Medium 4x4, and Hard 5x5 screens.

The solver metrics did not change during this pass, so the algorithm comparison table above remains current.

# Manual Verification Reaffirming the Results #

Personal filesystem paths in the prompts below have been replaced with a generic project path. Commands and measured results are unchanged.
        Below is a copy and paste of terminal outputs after running the following commands in sequence:

        python 02_python_solver.py
        python 03_verify_solver.py
        python -m unittest discover -v

        Windows PowerShell
        Copyright (C) Microsoft Corporation. All rights reserved.

        PS C:\Projects\search-and-verification-sliding-tile-puzzle\text_only_python_solver> python 02_python_solver.py
        ============================================================
        AI SEARCH ASSIGNMENT — PYTHON SLIDING-TILE SOLVER
        ============================================================

        Sample 3x3 state:
        1  2  3
        7 __  6
        5  4  8

        Representation: immutable flat tuple[int, ...]
        Blank: 0
        Moves: UP, DOWN, LEFT, RIGHT describe blank movement
        A* tie-breaking: lowest f, then lowest h, then insertion order

        ------------------------------------------------------------
        Algorithm: BFS
        Solved: True
        Status: solved
        Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
        Solution length: 6
        Expanded states: 48
        Message: Puzzle solved.
        ------------------------------------------------------------
        Algorithm: A* Misplaced
        Solved: True
        Status: solved
        Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
        Solution length: 6
        Expanded states: 8
        Message: Puzzle solved.
        ------------------------------------------------------------
        Algorithm: A* Manhattan
        Solved: True
        Status: solved
        Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
        Solution length: 6
        Expanded states: 6
        Message: Puzzle solved.
        PS C:\Projects\search-and-verification-sliding-tile-puzzle\text_only_python_solver> python 03_verify_solver.py

        ============================================================
        TEST 1 — SOLVED PUZZLE
        ======================
        Starting state:
        1  2  3
        4  5  6
        7  8 __
        Algorithm: BFS
        Solved: True
        Move sequence: (empty)
        Solution length: 0
        Expanded states: 0

        ============================================================
        TEST 2 — ONE MOVE FROM GOAL
        ===========================
        Starting state:
        1  2  3
        4  5  6
        7 __  8
        Algorithm: BFS
        Solved: True
        Move sequence: RIGHT
        Solution length: 1
        Expanded states: 1

        ============================================================
        TEST 3 — SEVERAL MOVES FROM GOAL
        ================================
        Starting state:
        1  2  3
        __  4  6
        7  5  8
        Algorithm: BFS
        Solved: True
        Move sequence: RIGHT, DOWN, RIGHT
        Solution length: 3
        Expanded states: 8

        ============================================================
        TEST 4 — INVALID PUZZLE
        =======================
        Starting state tuple:
        (1, 2, 3, 4, 5, 6, 7, 7, 0)
        BFS: solved=False, status=invalid, message=Board contains duplicate tile value(s): [7].
        A* Misplaced: solved=False, status=invalid, message=Board contains duplicate tile value(s): [7].
        A* Manhattan: solved=False, status=invalid, message=Board contains duplicate tile value(s): [7].

        ============================================================
        TEST 5 — UNSOLVABLE PUZZLE
        ==========================
        Starting state tuple:
        (1, 2, 3, 4, 5, 6, 8, 7, 0)
        BFS: solved=False, status=unsolvable, message=Puzzle is structurally valid but unsolvable.
        A* Misplaced: solved=False, status=unsolvable, message=Puzzle is structurally valid but unsolvable.
        A* Manhattan: solved=False, status=unsolvable, message=Puzzle is structurally valid but unsolvable.

        ============================================================
        BFS VS A* COMPARISON
        ====================
        Starting state:
        1  2  3
        7 __  6
        5  4  8
        Constructed from legal blank moves: LEFT, UP, LEFT, DOWN, RIGHT, UP

        Starting state:
        1  2  3
        7 __  6
        5  4  8
        Algorithm: BFS
        Solved: True
        Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
        Solution length: 6
        Expanded states: 48

        Starting state:
        1  2  3
        7 __  6
        5  4  8
        Algorithm: A* Misplaced
        Solved: True
        Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
        Solution length: 6
        Expanded states: 8

        Starting state:
        1  2  3
        7 __  6
        5  4  8
        Algorithm: A* Manhattan
        Solved: True
        Move sequence: DOWN, LEFT, UP, RIGHT, DOWN, RIGHT
        Solution length: 6
        Expanded states: 6

        Algorithm | Solution Length | Expanded States
        BFS | 6 | 48
        A* Misplaced | 6 | 8
        A* Manhattan | 6 | 6

        All verification assertions passed.
        PS C:\Projects\search-and-verification-sliding-tile-puzzle\text_only_python_solver> python -m unittest discover -v
        test_ascii_fallback_uses_plain_dash_and_ascii_blank (tests.test_cli_helpers.CliHelperTests.test_ascii_fallback_uses_plain_dash_and_ascii_blank) ... ok
        test_comparison_state_is_fixed_reasonable_3x3_state (tests.test_cli_helpers.CliHelperTests.test_comparison_state_is_fixed_reasonable_3x3_state) ... ok
        test_normalize_command_trims_and_uppercases_input (tests.test_cli_helpers.CliHelperTests.test_normalize_command_trims_and_uppercases_input) ... ok
        test_render_game_screen_keeps_metrics_and_fact_readable (tests.test_cli_helpers.CliHelperTests.test_render_game_screen_keeps_metrics_and_fact_readable) ... ok
        test_save_completion_prints_success_banner_without_real_record_file (tests.test_cli_helpers.CliHelperTests.test_save_completion_prints_success_banner_without_real_record_file) ... ok
        test_default_facts_cover_required_topics (tests.test_facts.FactRotationTests.test_default_facts_cover_required_topics) ... ok
        test_fact_index_rotates_by_elapsed_time_without_threads (tests.test_facts.FactRotationTests.test_fact_index_rotates_by_elapsed_time_without_threads) ... ok
        test_fact_rotation_rejects_bad_inputs (tests.test_facts.FactRotationTests.test_fact_rotation_rejects_bad_inputs) ... ok
        test_rotation_interval_is_thirty_seconds (tests.test_facts.FactRotationTests.test_rotation_interval_is_thirty_seconds) ... ok
        test_generates_supported_sizes_without_size_specific_logic (tests.test_generator.PuzzleGeneratorTests.test_generates_supported_sizes_without_size_specific_logic) ... ok
        test_generates_valid_solvable_non_goal_puzzles_for_difficulties (tests.test_generator.PuzzleGeneratorTests.test_generates_valid_solvable_non_goal_puzzles_for_difficulties) ... ok
        test_rejects_unknown_difficulty (tests.test_generator.PuzzleGeneratorTests.test_rejects_unknown_difficulty) ... ok
        test_rejects_unsupported_size_and_zero_scramble (tests.test_generator.PuzzleGeneratorTests.test_rejects_unsupported_size_and_zero_scramble) ... ok
        test_blank_does_not_contribute_to_heuristics (tests.test_heuristics.HeuristicTests.test_blank_does_not_contribute_to_heuristics) ... ok
        test_heuristics_are_dimension_aware (tests.test_heuristics.HeuristicTests.test_heuristics_are_dimension_aware) ... ok
        test_heuristics_are_zero_at_3x3_goal (tests.test_heuristics.HeuristicTests.test_heuristics_are_zero_at_3x3_goal) ... ok
        test_heuristics_are_zero_at_generalized_goals (tests.test_heuristics.HeuristicTests.test_heuristics_are_zero_at_generalized_goals) ... ok
        test_known_non_goal_heuristic_values (tests.test_heuristics.HeuristicTests.test_known_non_goal_heuristic_values) ... ok
        test_apply_move_rejects_off_board_and_unknown_moves (tests.test_model.PuzzleModelTests.test_apply_move_rejects_off_board_and_unknown_moves) ... ok
        test_apply_move_uses_blank_movement_semantics (tests.test_model.PuzzleModelTests.test_apply_move_uses_blank_movement_semantics) ... ok
        test_dimension_and_coordinate_conversion (tests.test_model.PuzzleModelTests.test_dimension_and_coordinate_conversion) ... ok
        test_equality_and_hash_use_immutable_tuple_state (tests.test_model.PuzzleModelTests.test_equality_and_hash_use_immutable_tuple_state) ... ok
        test_goal_boards_for_supported_sizes (tests.test_model.PuzzleModelTests.test_goal_boards_for_supported_sizes) ... ok
        test_goal_recognition (tests.test_model.PuzzleModelTests.test_goal_recognition) ... ok
        test_legal_moves_from_corner (tests.test_model.PuzzleModelTests.test_legal_moves_from_corner) ... ok
        test_legal_moves_from_edge (tests.test_model.PuzzleModelTests.test_legal_moves_from_edge) ... ok
        test_legal_moves_from_interior (tests.test_model.PuzzleModelTests.test_legal_moves_from_interior) ... ok
        test_successors_pair_moves_with_new_states (tests.test_model.PuzzleModelTests.test_successors_pair_moves_with_new_states) ... ok
        test_terminal_rendering_supports_unicode_and_ascii_blank (tests.test_model.PuzzleModelTests.test_terminal_rendering_supports_unicode_and_ascii_blank) ... ok
        test_append_load_and_filter_records_by_username (tests.test_records.CompletionRecordTests.test_append_load_and_filter_records_by_username) ... ok
        test_format_elapsed_time_rejects_invalid_values (tests.test_records.CompletionRecordTests.test_format_elapsed_time_rejects_invalid_values) ... ok
        test_load_records_handles_missing_empty_and_malformed_files (tests.test_records.CompletionRecordTests.test_load_records_handles_missing_empty_and_malformed_files) ... ok
        test_save_records_validates_before_writing (tests.test_records.CompletionRecordTests.test_save_records_validates_before_writing) ... ok
        test_validation_rejects_bad_completion_data (tests.test_records.CompletionRecordTests.test_validation_rejects_bad_completion_data) ... ok
        test_a_star_algorithms_match_bfs_solution_lengths (tests.test_search.AStarSearchTests.test_a_star_algorithms_match_bfs_solution_lengths) ... ok
        test_a_star_handles_already_solved_state (tests.test_search.AStarSearchTests.test_a_star_handles_already_solved_state) ... ok
        test_a_star_returns_invalid_and_unsolvable_results (tests.test_search.AStarSearchTests.test_a_star_returns_invalid_and_unsolvable_results) ... ok
        test_invalid_state_returns_invalid_result (tests.test_search.AStarSearchTests.test_invalid_state_returns_invalid_result) ... ok
        test_returned_sequence_reaches_goal_for_comparison_style_case (tests.test_search.AStarSearchTests.test_returned_sequence_reaches_goal_for_comparison_style_case) ... ok
        test_several_move_state_returns_expected_minimum_length (tests.test_search.AStarSearchTests.test_several_move_state_returns_expected_minimum_length) ... ok
        test_unsolvable_state_returns_unsolvable_result (tests.test_search.AStarSearchTests.test_unsolvable_state_returns_unsolvable_result) ... ok
        test_one_move_state_returns_minimum_length_one (tests.test_search.BreadthFirstSearchTests.test_one_move_state_returns_minimum_length_one) ... ok
        test_solved_state_returns_empty_sequence (tests.test_search.BreadthFirstSearchTests.test_solved_state_returns_empty_sequence) ... ok
        test_reconstruct_moves_returns_start_to_goal_order (tests.test_search.SearchResultTests.test_reconstruct_moves_returns_start_to_goal_order) ... ok
        test_solved_result_normalizes_solution_length (tests.test_search.SearchResultTests.test_solved_result_normalizes_solution_length) ... ok
        test_5x5_solvability_sanity (tests.test_validation.ValidationTests.test_5x5_solvability_sanity) ... ok
        test_inversion_and_blank_row_helpers (tests.test_validation.ValidationTests.test_inversion_and_blank_row_helpers) ... ok
        test_known_3x3_solvable_and_unsolvable (tests.test_validation.ValidationTests.test_known_3x3_solvable_and_unsolvable) ... ok
        test_known_4x4_solvable_and_unsolvable_parity (tests.test_validation.ValidationTests.test_known_4x4_solvable_and_unsolvable_parity) ... ok
        test_rejects_duplicate_tile (tests.test_validation.ValidationTests.test_rejects_duplicate_tile) ... ok
        test_rejects_missing_blank (tests.test_validation.ValidationTests.test_rejects_missing_blank) ... ok
        test_rejects_missing_tile (tests.test_validation.ValidationTests.test_rejects_missing_tile) ... ok
        test_rejects_multiple_blanks (tests.test_validation.ValidationTests.test_rejects_multiple_blanks) ... ok
        test_rejects_non_integer_tiles (tests.test_validation.ValidationTests.test_rejects_non_integer_tiles) ... ok
        test_rejects_out_of_range_tile (tests.test_validation.ValidationTests.test_rejects_out_of_range_tile) ... ok
        test_rejects_size_length_mismatch (tests.test_validation.ValidationTests.test_rejects_size_length_mismatch) ... ok
        test_rejects_wrong_length (tests.test_validation.ValidationTests.test_rejects_wrong_length) ... ok
        test_valid_boards_for_supported_sizes (tests.test_validation.ValidationTests.test_valid_boards_for_supported_sizes) ... ok

        ----------------------------------------------------------------------
        Ran 58 tests in 0.093s

