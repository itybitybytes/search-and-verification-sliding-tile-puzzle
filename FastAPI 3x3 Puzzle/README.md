# Sliding Tile Puzzle Solver

Python sliding-tile puzzle solver and FastAPI web application for the graded AI search assignment.

## A. Required Assignment Files

The required submission artifacts are kept at the repository root:

- `01_LLM_SPECIFICATION.md` — original project/specification decisions.
- `02_python_solver.py` — reviewer-facing Python solver entry point.
- `03_verify_solver.py` — directly runnable verification script.
- `04_TEST_EVIDENCE.md` — real output captured from the verification script.
- `05_REQUIREMENTS_TRACEABILITY.md` — requirement-by-requirement traceability.

## B. How To Run Solver

Run the solver facade directly:

```bash
python 02_python_solver.py
```

The reusable solver implementation lives in `solver/`. The facade exposes the core board model, validation, solvability checks, BFS, A* with misplaced tiles, A* with Manhattan distance, returned move sequences, solution lengths, and expanded-state counts.

## C. How To Run Verification

Run the required verification artifact:

```bash
python 03_verify_solver.py
```

This executes the fixed 3x3 solved, one-move, several-move, invalid, unsolvable, and algorithm-comparison cases using real solver results.

## D. How To Run Web Application Locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the FastAPI application:

```bash
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

The web server also provides:

- `/health`
- `/api/config`
- `/api/new-puzzle?difficulty=easy`
- `/api/solver-demo?case=comparison`
- `/api/completions`

## E. Database / Environment Variables

Completion records are stored server-side with SQLite through Python's standard `sqlite3` library.

Environment variable:

```text
PUZZLE_COMPLETIONS_DB
```

Local default when unset:

```text
data/completions.sqlite3
```

Render persistent-disk example:

```text
PUZZLE_COMPLETIONS_DB=/var/data/completions.sqlite3
```

The app creates the database schema automatically on first write. No database password or secret is committed. This project does not use `DATABASE_URL`; the selected architecture uses a SQLite file path controlled by `PUZZLE_COMPLETIONS_DB`.

## F. How To Deploy On Render

1. Push the repository to GitHub.
2. In Render, create a new Blueprint or Web Service from the GitHub repository.
3. Use the included `render.yaml`, or configure the same settings manually.
4. Build command:

```bash
pip install -r requirements.txt
```

5. Start command:

```bash
uvicorn web.app:app --host 0.0.0.0 --port $PORT
```

6. Add a persistent disk mounted at:

```text
/var/data
```

7. Set:

```text
PUZZLE_COMPLETIONS_DB=/var/data/completions.sqlite3
```

Render supplies `PORT`; the start command binds Uvicorn to that value. Static files are served from `web/static` through FastAPI's `StaticFiles` mount at `/static`.

## G. Game Features

- Easy 3x3, Medium 4x4, and Hard 5x5 playable boards.
- Solvable puzzle generation by randomized legal moves from the goal state.
- Drag/click tile controls with legal-move validation.
- Move counter and elapsed timer.
- Username-associated persistent completion records.
- Rotating `DID YOU KNOW...` facts.
- Invalid-move buzz and temporary red shake feedback.
- Completion celebration sound and confetti.
- Decorative axe decal in the blank position.
- Dedicated 3x3 assignment solver demonstration for BFS, A* misplaced tiles, and A* Manhattan distance.

## Static And Audio Asset Handling

The visual axe decal is rendered in the browser as a decorative character in the blank tile; it is not a Python puzzle-state value and does not require a separate image file.

The invalid buzz and celebration sound are synthesized with the browser Web Audio API. There are no external audio files, no third-party media licenses, and no audio asset paths to configure for deployment. Audio starts only after browser interaction when allowed by autoplay rules and fails gracefully if blocked.

## Development Checks

Run all automated tests:

```bash
python -m unittest discover
```

Run the required verification script:

```bash
python 03_verify_solver.py
```

Run a web startup smoke test:

```bash
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```
