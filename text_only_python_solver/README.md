# Text-Only Python Sliding Puzzle Solver

This is a standalone text-only Python sliding-puzzle implementation.

It is intentionally separate from any browser project:

- NO FASTAPI
- NO SERVER
- NO WEB UI
- NO HTML/CSS/JS
- NO DATABASE SERVICE

The project uses normal Python terminal I/O, standard-library `unittest`, and local JSON files for optional completion records.

## Required Assignment Artifacts

The required graded artifacts are kept at the subproject root:

- `01_LLM_SPECIFICATION.md`
- `02_python_solver.py`
- `03_verify_solver.py`
- `04_TEST_EVIDENCE.md`
- `05_REQUIREMENTS_TRACEABILITY.md`

## Commands

Run the reviewer-facing solver demonstration:

```text
python 02_python_solver.py
```

Run the required verification script:

```text
python 03_verify_solver.py
```

Run the playable terminal game:

```text
python 06_cli_game.py
```

Run the complete automated test suite:

```text
python -m unittest discover -v
```

## Puzzle Rules And Representation

Supported playable difficulties:

- Easy = 3x3
- Medium = 4x4
- Hard = 5x5

Goal:

- Numbered tiles are in ascending row-major order.
- The blank is in the lower-right corner.

Board representation:

- Immutable flat `tuple[int, ...]`
- Row-major order
- Exactly `N*N` entries
- Internal blank representation is integer `0`

Axe:

- The axe is only a visual representation of the blank in terminal output.
- The puzzle engine still stores the blank as `0`.
- The axe never counts as a numbered tile or heuristic value.

Moves:

- `UP`
- `DOWN`
- `LEFT`
- `RIGHT`

Move directions describe movement of the blank. For example, `LEFT` means the blank swaps with the tile immediately to its left.

## Solver

The solver implements:

- Breadth-first search
- A* with misplaced-tiles heuristic
- A* with Manhattan-distance heuristic

Returned solver results include:

- algorithm name
- solved status
- ordered move sequence
- solution length
- expanded-state count
- status/message

Practical graded search verification focuses on reasonable 3x3 states. The underlying puzzle model is dimension-aware for 3x3, 4x4, and 5x5, but this project does not claim arbitrary 4x4 or 5x5 BFS practicality.

## Terminal Game Features

`06_cli_game.py` provides:

- username prompt
- Easy/Medium/Hard puzzle play
- guaranteed-solvable puzzle generation by legal scrambling from the goal
- timer
- move counter
- local JSON completion records
- Did You Know facts
- invalid-move feedback
- success celebration
- solver demonstration menu
- optional solver move step-through

Completion records are stored locally in:

```text
completion_records.json
```

The file is created only after a completed puzzle is saved.

## Did You Know Facts

Facts cover sliding puzzles, BFS, A*, Manhattan distance, misplaced tiles, heuristics, state spaces, and optimal search.

The rotation rule is deterministic:

```text
floor(elapsed_seconds / 30) % len(facts)
```

No background thread is used.

## ASCII Fallback

By default, Unicode-capable terminals show the blank as an axe. To force ASCII-safe output:

```text
set PUZZLE_ASCII=1
python 06_cli_game.py
```

In ASCII mode, the blank renders as:

```text
__
```
