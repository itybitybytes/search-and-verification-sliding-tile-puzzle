# Search and Verification: Sliding-Tile Puzzle

A Python AI search assignment exploring the sliding-tile puzzle through breadth-first search (BFS), A* with misplaced tiles, and A* with Manhattan distance. The project includes reproducible solver verification and two independently runnable applications: a text-only terminal program and a FastAPI browser application.

**For grading, begin with [`text_only_python_solver/`](text_only_python_solver/).** It contains the primary assignment submission, verification evidence, reflection, and concept responses. The FastAPI application is an additional web-based extension.

## Choose a Version

| | Text-only assignment | Web application extension |
| --- | --- | --- |
| Folder | [`text_only_python_solver/`](text_only_python_solver/) | [`FastAPI 3x3 Puzzle/`](FastAPI%203x3%20Puzzle/) |
| Interface | Command Prompt, PowerShell, or another terminal | Browser |
| Runtime | Python standard library | Python, FastAPI, and Uvicorn |
| Manual puzzles | Easy 3x3, Medium 4x4, Hard 5x5 | Easy 3x3, Medium 4x4, Hard 5x5 |
| Search demonstration | Reasonable 3x3 cases | Fixed reasonable 3x3 cases |
| Completion storage | Local JSON file | Server-side SQLite file |
| Hosting | Runs locally; no server needed | Local web service or Render |

The text-only program has no FastAPI, HTML, CSS, JavaScript, web server, or database-service dependency. Neither version needs the other version to run.

## Repository Guide

```text
search-and-verification-sliding-tile-puzzle/
|-- README.md
|-- text_only_python_solver/            Primary graded submission
|   |-- 01_LLM_SPECIFICATION.md
|   |-- 02_python_solver.py
|   |-- 03_verify_solver.py
|   |-- 04_TEST_EVIDENCE.md
|   |-- 05_REQUIREMENTS_TRACEABILITY.md
|   |-- 06_cli_game.py
|   |-- README.md
|   |-- HOW_TO_DEPLOY_TEXT_ONLY.txt
|   |-- REFLECTION.txt
|   |-- CONCEPT AND VERIFICATION QUESTIONS.txt
|   |-- puzzle/                         Model, search, and game support
|   `-- tests/
|-- FastAPI 3x3 Puzzle/                 Optional web extension
|   |-- 01_LLM_SPECIFICATION.md
|   |-- 02_python_solver.py
|   |-- 03_verify_solver.py
|   |-- 04_TEST_EVIDENCE.md
|   |-- 05_REQUIREMENTS_TRACEABILITY.md
|   |-- README.md
|   |-- How_to_Local_Deploy.txt
|   |-- requirements.txt
|   |-- render.yaml
|   |-- solver/                         Python solver implementation
|   |-- web/                            FastAPI and browser application
|   `-- tests/
`-- Read Me Please (API vs Text Only).txt
```

The directory named `3x3 Puzzle Text Solver (IGNORE ME)` is an unfinished earlier demo. It is not the grading target or a required dependency. Use the source folders above rather than the ZIP archive when reviewing the project.

## Assignment Artifacts

The following files are at the root of the **text-only subproject**:

| Artifact | Purpose |
| --- | --- |
| [01_LLM_SPECIFICATION.md](text_only_python_solver/01_LLM_SPECIFICATION.md) | Assignment requirements and documented design decisions |
| [02_python_solver.py](text_only_python_solver/02_python_solver.py) | Reviewer-facing solver entry point and noninteractive demonstration |
| [03_verify_solver.py](text_only_python_solver/03_verify_solver.py) | Runnable verification using fixed puzzle cases |
| [04_TEST_EVIDENCE.md](text_only_python_solver/04_TEST_EVIDENCE.md) | Recorded results, move sequences, and algorithm comparisons |
| [05_REQUIREMENTS_TRACEABILITY.md](text_only_python_solver/05_REQUIREMENTS_TRACEABILITY.md) | Mapping of R01-R31 to implementation and verification |

Additional assignment responses are in [REFLECTION.txt](text_only_python_solver/REFLECTION.txt) and [CONCEPT AND VERIFICATION QUESTIONS.txt](text_only_python_solver/CONCEPT%20AND%20VERIFICATION%20QUESTIONS.txt).

The web subproject maintains its own specification, solver facade, verification script, evidence, and traceability. Review each evidence file alongside its corresponding implementation.

## Run the Text-Only Program

Use Python 3.10 or newer. Download and extract the repository, or clone it using the URL shown by GitHub's **Code** button. Open a terminal in the extracted or cloned repository root.

Enter the text-only folder and confirm Python is available:

```shell
cd text_only_python_solver
python --version
```

No third-party packages need to be installed for this version.

Run the playable program:

```shell
python 06_cli_game.py
```

Enter a username, then choose from:

1. Play Puzzle
2. Solver Demonstration
3. View My Completion Records
4. Help
5. Quit

Manual play supports Easy (3x3), Medium (4x4), and Hard (5x5). Enter `UP`, `DOWN`, `LEFT`, or `RIGHT` to move the blank. Commands are case-insensitive. `HELP`, `NEW`, and `QUIT` are also available during play.

The game displays the username, difficulty, successful move count, elapsed time, and a puzzle-related fact. Invalid moves leave both the board and move count unchanged. Completing a puzzle preserves the final result, displays a celebration, and saves a username-associated record in `completion_records.json` in the text-only folder.

The timer and facts update when the terminal screen redraws. Fact selection advances in 30-second elapsed-time intervals without a background thread.

If `python` is unavailable on Windows but the Python launcher is installed, substitute `py` in these commands. On systems where Python 3 is named `python3`, use that command instead.

### ASCII Output

The blank can display as an axe in a Unicode-capable terminal. It remains the integer `0` in the puzzle state. If the symbol does not display correctly, enable the ASCII fallback, which renders the blank as `__`.

PowerShell:

```powershell
$env:PUZZLE_ASCII="1"
python 06_cli_game.py
```

Windows Command Prompt:

```bat
set PUZZLE_ASCII=1
python 06_cli_game.py
```

See [HOW_TO_DEPLOY_TEXT_ONLY.txt](text_only_python_solver/HOW_TO_DEPLOY_TEXT_ONLY.txt) for the longer command-prompt walkthrough. Sharing this program means sharing the complete text-only folder; it does not require web deployment.

## Run Search and Verification

From `text_only_python_solver/`, run:

```shell
python 02_python_solver.py
python 03_verify_solver.py
python -m unittest discover -v
```

The first command demonstrates all three algorithms. The second runs the fixed solved, one-move, several-move, invalid, unsolvable, and comparison cases. The third runs the automated test suite.

Verification checks legal move replay, reaching the goal, agreement between reported length and move-sequence length, expected simple-case lengths, heuristic values at the goal, invalid/unsolvable handling, and agreement between the algorithms on the comparison case. Output includes actual solution lengths and expanded-state counts.

Recorded measurements are in [04_TEST_EVIDENCE.md](text_only_python_solver/04_TEST_EVIDENCE.md). Run the commands above for results from your checkout; this README does not substitute a static metric table for execution.

The interactive Solver Demonstration menu also displays full move sequences and offers step-through inspection.

## Puzzle and Search Design

The N-puzzle consists of an N x N board with numbered tiles and one blank. A legal move exchanges the blank with one immediately adjacent tile horizontally or vertically. Diagonal and off-board moves are prohibited.

The state is an immutable, hashable flat tuple of integers in row-major order. The blank is `0`. The goal is ascending numbered tiles followed by the blank in the lower-right corner:

```text
1 2 3
4 5 6
7 8 0

(1, 2, 3, 4, 5, 6, 7, 8, 0)
```

`UP`, `DOWN`, `LEFT`, and `RIGHT` describe **blank movement**. For example, `UP` swaps the blank with the tile directly above it. Board movement and goal construction derive from the dimension, row, and column; the same model supports 3x3, 4x4, and 5x5.

| Algorithm | Search rule |
| --- | --- |
| BFS | FIFO traversal by increasing depth; unit-cost moves yield a minimum-move solution |
| A* Misplaced | Prioritizes `f = g + h`, where `h` counts nonblank tiles outside their goal positions |
| A* Manhattan | Prioritizes `f = g + h`, where `h` sums nonblank tiles' row and column distances from their goal positions |

Both heuristics exclude the blank and return zero at the goal. A* ties resolve by lowest `f`, then lowest `h`, then earliest insertion order using a monotonic counter.

BFS records discovered states to avoid redundant visits. A* maintains best-known path costs and skips stale frontier entries. Shared predecessor reconstruction produces the ordered move sequence. Results expose algorithm, solved status, moves, solution length, expanded states, and status/message.

A state counts as expanded when it is popped for processing and the algorithm proceeds to generate or examine successors. A goal recognized before successor generation is not counted as expanded.

Validation checks dimension coherence, board length, tile values, duplicates, missing tiles, and exactly one blank. Solvability checking uses inversion parity for odd widths and inversion parity together with the blank's row from the bottom for even widths. Manual puzzles are generated by legal scrambling from the goal.

**Practical graded search verification focuses on reasonable 3x3 states.** Supporting larger boards for manual play does not imply that arbitrary 4x4 or 5x5 BFS/A* searches are practical.

### Code Review Map

| Text-only file | Responsibility |
| --- | --- |
| `puzzle/model.py` | State representation, dimensions, goal, legal movement, successors, and rendering |
| `puzzle/validation.py` | Malformed-board rejection and solvability parity |
| `puzzle/search.py` | BFS and the shared A* engine with public heuristic-specific entry points |
| `puzzle/heuristics.py` | Misplaced tiles and Manhattan distance |
| `puzzle/results.py` | Search results and path reconstruction |
| `puzzle/generator.py` | Solvable manual-game generation |
| `puzzle/records.py` | Local JSON completion storage and username filtering |
| `puzzle/facts.py` | Fact content and elapsed-time selection |
| `06_cli_game.py` | Terminal menus, gameplay, timing, and solver inspection |
| `tests/` | Automated coverage |

## Run the Web Extension

Start from the repository root in a separate terminal. Create an isolated environment inside the web folder:

```shell
cd "FastAPI 3x3 Puzzle"
python -m venv .venv
```

On Windows PowerShell or Command Prompt, these commands use the environment directly without requiring activation:

```shell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

On macOS/Linux:

```shell
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Stop the server with `Ctrl+C`.

The browser application provides a large dimension-aware board, drag/click controls, an axe blank, difficulty controls, timer, moves, username entry, rotating facts, invalid-move feedback, and completion effects. A separate demonstration area compares the three solvers on fixed 3x3 cases.

FastAPI serves the page and static files from `web/static`. The buzz and celebration sounds are synthesized through the browser Web Audio API; they do not require downloaded audio assets. Playback depends on browser interaction and audio permissions.

| Route | Purpose |
| --- | --- |
| `GET /` | Browser application |
| `GET /health` | Service health |
| `GET /api/config` | Difficulty and application configuration |
| `GET /api/new-puzzle?difficulty=easy` | Legal-scramble puzzle generation; also accepts `medium` and `hard` |
| `GET /api/solver-demo?case=comparison` | Fixed 3x3 solver comparison; also accepts `solved` and `several` |
| `POST /api/completions` | Validate and store completion data |

For web verification on Windows, run from the web folder:

```shell
.venv\Scripts\python.exe 03_verify_solver.py
.venv\Scripts\python.exe -m unittest discover -v
```

Use `.venv/bin/python` for the equivalent macOS/Linux commands. See the [web README](FastAPI%203x3%20Puzzle/README.md) and [local deployment walkthrough](FastAPI%203x3%20Puzzle/How_to_Local_Deploy.txt) for additional details.

## Web Persistence and Render Configuration

The web application uses SQLite through Python's standard `sqlite3` library. `PUZZLE_COMPLETIONS_DB` sets the database file path; the local default is `data/completions.sqlite3`. It does not use `DATABASE_URL` or require a separate PostgreSQL service.

For a Render Web Service using this whole repository, configure the working root as **`FastAPI 3x3 Puzzle`**. The checked-in configuration provides these commands and storage settings:

| Setting | Value |
| --- | --- |
| Root Directory | `FastAPI 3x3 Puzzle` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn web.app:app --host 0.0.0.0 --port $PORT` |
| Health endpoint | `/health` |
| Persistent disk mount | `/var/data` |
| `PUZZLE_COMPLETIONS_DB` | `/var/data/completions.sqlite3` |

The [render.yaml](FastAPI%203x3%20Puzzle/render.yaml) file lives inside the web subfolder and currently has no `rootDir` setting. Its relative commands assume the web folder is the service root. For this combined repository, use the manual Web Service settings above rather than assuming the nested Blueprint runs unchanged from the repository root.

Keep the SQLite database on persistent storage to retain completion history across deployments. Usernames are labels rather than authenticated accounts, and the completion endpoint validates submitted fields rather than independently proving an entire game was played. There is no public leaderboard.

## Data and Sharing

The terminal program stores records locally in JSON; the web program stores records in server-side SQLite. They do not synchronize completion histories. Keep personal runtime records, database files, environment files, virtual environments, and caches out of source-control submissions.

To distribute only the graded terminal program, share the complete `text_only_python_solver/` folder, including its supporting `puzzle/` package. To distribute both applications, share the repository with the two source folders intact.

The assignment specification and reflection document the AI-assisted development work.
