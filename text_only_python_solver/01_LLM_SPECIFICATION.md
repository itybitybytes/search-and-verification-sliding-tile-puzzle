# 01 LLM Specification

**Pre-implementation artifact:** This document is the original LLM specification for the sliding-tile puzzle project. It is intentionally written before any implementation code, tests, configuration, database schema, frontend files, or deployment files are created.

This specification is a graded submission artifact. It defines what a future implementation LLM should build after the user-controlled decisions listed in this document have been resolved.

## 1. Project Purpose

Build a web-based sliding-tile puzzle application backed by Python.

The project has two related purposes:

1. Provide a playable graphical sliding-puzzle web application.
2. Provide a graded Python search-algorithm implementation demonstrating breadth-first search and A* search.

The playable application must support three board sizes:

- Easy: 3x3
- Medium: 4x4
- Hard: 5x5

All three playable board sizes must share the same generalized puzzle and game architecture. The solver and verification requirements are focused on reasonable 3x3 puzzle cases. The implementation must not imply that breadth-first search is expected to efficiently solve arbitrary 4x4 or 5x5 puzzles.

## 2. Required Deliverables

The final project must include the following graded artifacts:

- This original LLM specification file: `01_LLM_SPECIFICATION.md`.
- A Python 3x3 sliding-tile puzzle solver.
- A runnable test or verification script.
- Test evidence or results showing the required verification cases and algorithm comparisons.
- A web-based playable sliding-tile puzzle application backed by Python.
- Deployment-ready project structure suitable for GitHub and Render.

No implementation deliverables may be created as part of this specification-only prompt.

## 3. Functional Requirements

The future implementation must:

- Generate solvable sliding-tile puzzles for 3x3, 4x4, and 5x5 boards.
- Allow a user to play the puzzle in a graphical browser interface.
- Support click, tap, and drag-style tile interaction.
- Track and display a move counter.
- Track and display a running puzzle timer.
- Stop the timer when the puzzle is completed.
- Associate completed puzzle times with a username.
- Persist completion records.
- Provide a Python search solver for 3x3 puzzle states.
- Implement BFS.
- Implement A* using misplaced-tiles heuristic.
- Implement A* using Manhattan-distance heuristic.
- Provide a way to display or inspect returned move sequences.
- Track solution length for each solver run.
- Track expanded states for each solver run.
- Detect invalid puzzle states.
- Detect unsolvable puzzle states.
- Provide runnable verification evidence for required cases.

## 4. Puzzle Rules

The sliding puzzle consists of numbered tiles and one blank space.

Rules:

- A numbered tile may move only into the adjacent blank space.
- Adjacency is orthogonal only: up, down, left, or right.
- Diagonal moves are not legal.
- A valid move changes the board state by swapping one numbered tile with the blank.
- An invalid manual move must leave the board state unchanged.
- Valid manual moves increment the move counter.
- Invalid manual moves do not increment the move counter.
- The puzzle is complete only when all numbered tiles are in ascending order and the blank is in the lower-right position.

Playable board dimensions are restricted to exactly:

- 3x3
- 4x4
- 5x5

No other board sizes are part of the required project.

## 5. Goal State

The user has already selected the goal orientation.

ASSIGNMENT REQUIREMENT R04 — GOAL STATE

The goal state is:

- Numbered tiles in ascending order.
- Blank position in the lower-right corner.
- For an N x N board, numbered tiles are ascending from `1` through `N*N - 1`, followed by `0`.
- The GUI visually shows a small axe decal in the blank position.
- The axe is decorative only.
- The axe must never count as a numbered tile.
- The axe must never count as a heuristic value.
- The axe must not affect solvability, legal moves, solution length, expanded-state counts, or goal-state checks.

For a 3x3 board, the exact goal state is:

```python
(1, 2, 3,
 4, 5, 6,
 7, 8, 0)
```

For a 4x4 board, the exact goal state is:

```python
(1, 2, 3, 4,
 5, 6, 7, 8,
 9, 10, 11, 12,
 13, 14, 15, 0)
```

For a 5x5 board, the exact goal state is numbered tiles 1 through 24 in row-major ascending order, followed by `0` in the lower-right blank position.

## 6. Board-Size Generalization

The implementation must use a generalized architecture that can represent and operate on 3x3, 4x4, and 5x5 boards without duplicating separate puzzle logic for each size.

The implementation should separate:

- Board dimension.
- Tile values.
- Blank position.
- Legal-move generation.
- Goal-state generation.
- Solvability validation.
- Search logic.
- Web rendering.

The graded solver evidence is focused on 3x3 boards. The design must make adapting the solver to 4x4 straightforward, but BFS is not required to efficiently solve arbitrary 4x4 or 5x5 states.

## 7. Board Representation

ASSIGNMENT REQUIREMENT R05 — BOARD REPRESENTATION

The Python puzzle board representation is an immutable flat tuple of integers.

The tuple has exactly `N*N` entries for an N x N board. Tiles are stored in row-major order. The board dimension is provided or inferred consistently by the puzzle-state APIs from the tuple length when the length is a supported perfect square.

Examples:

3x3:

```python
(1, 2, 3,
 4, 5, 6,
 7, 8, 0)
```

4x4:

```python
(1, 2, 3, 4,
 5, 6, 7, 8,
 9, 10, 11, 12,
 13, 14, 15, 0)
```

Rationale:

- Immutable.
- Hashable.
- Appropriate for visited and discovered sets.
- Easy to generalize to arbitrary N.
- Easy to convert between flat index and row/column coordinates.

Flat index and row/column conversion must use arithmetic based on the board dimension:

- `row = index // N`
- `col = index % N`
- `index = row * N + col`

Movement, goal checks, validation, heuristic functions, and search algorithms must use this generalized representation rather than hard-coded 3x3 state layouts.

## 8. Blank Representation

ASSIGNMENT REQUIREMENT — INTERNAL BLANK REPRESENTATION

The internal blank representation is integer `0`.

The browser GUI may visually display an axe decal for the blank, but the puzzle engine uses `0`.

The blank must never count as a numbered tile. It must be excluded from tile numbering, misplaced-tile counts, Manhattan-distance sums, solution-length calculations, and all other numeric tile logic.

## 9. Move Naming Convention

ASSIGNMENT REQUIREMENT R06 — MOVE NAMES

Use these exact move names:

- `UP`
- `DOWN`
- `LEFT`
- `RIGHT`

The directions describe movement of the blank, not movement of the numbered tile.

This distinction is required because tile movement and blank movement are opposites. For example:

- `UP` means the blank exchanges positions with the tile directly above it. Visually, that numbered tile moves down into the previous blank location.
- `DOWN` means the blank exchanges positions with the tile directly below it. Visually, that numbered tile moves up into the previous blank location.
- `LEFT` means the blank exchanges positions with the tile directly to its left. Visually, that numbered tile moves right into the previous blank location.
- `RIGHT` means the blank exchanges positions with the tile directly to its right. Visually, that numbered tile moves left into the previous blank location.

Returned move sequences, solver output, tests, logs, and any future GUI solver display must use these exact uppercase strings with blank-movement semantics.

## 10. Search Algorithms

The Python solver must implement:

- Breadth-first search.
- A* with misplaced-tiles heuristic.
- A* with Manhattan-distance heuristic.

All search algorithms must:

- Accept a valid 3x3 start state.
- Detect the selected goal state.
- Return a solution path when one exists.
- Report solution length.
- Report expanded-state count.
- Provide a way to inspect the returned move sequence.
- Handle already solved states.
- Handle states one move from the goal.
- Handle states several moves from the goal.
- Handle invalid or unsolvable input states.

The search implementation should be designed so adapting to 4x4 is straightforward, but 3x3 correctness and evidence are the required focus.

## 11. BFS Optimality Requirement

Breadth-first search must find a minimum-move solution for tested 3x3 puzzle states.

The BFS implementation must:

- Explore states in increasing solution depth.
- Avoid revisiting already-seen states.
- Return the first goal state reached only if BFS ordering guarantees that it is a minimum-move solution.
- Report solution length as the number of legal moves in the returned solution path.
- Provide evidence that BFS returns the expected minimum length for the required verification cases.

If the move-generation order affects which minimum-length solution is returned among multiple optimal solutions, that order must be documented after the move naming convention is resolved.

## 12. Misplaced-Tiles Heuristic

A* with misplaced-tiles heuristic must estimate distance by counting numbered tiles that are not in their goal positions.

Requirements:

- The blank must be ignored.
- The decorative axe must be ignored.
- The heuristic must equal zero at the goal state.
- The heuristic must not count the blank as misplaced.
- The heuristic must not count any GUI-only decoration.

For any valid 3x3 state, the misplaced-tiles value must be a nonnegative integer.

## 13. Manhattan-Distance Heuristic

A* with Manhattan-distance heuristic must estimate distance by summing each numbered tile's row and column distance from its goal position.

Requirements:

- The blank must be ignored.
- The decorative axe must be ignored.
- The heuristic must equal zero at the goal state.
- The heuristic must not include diagonal distance.
- The heuristic must not count any GUI-only decoration.

For any valid 3x3 state, the Manhattan-distance value must be a nonnegative integer.

## 14. A* Tie-Breaking

ASSIGNMENT REQUIREMENT R07 — A* TIE-BREAKING

Use deterministic priority ordering:

1. Lowest `f = g + h`.
2. If `f` ties, lowest `h`.
3. If both `f` and `h` tie, earliest insertion order.

Use a monotonically increasing insertion counter when required by the priority queue.

This rule is required because it:

- Produces deterministic results.
- Prevents Python from needing to compare puzzle-state objects directly.
- Prefers a state estimated closer to the goal when `f` values tie.

The same tie-breaking behavior must apply to both A* configurations:

- A* using misplaced-tiles heuristic.
- A* using Manhattan-distance heuristic.

## 15. Invalid-State Handling

ASSIGNMENT REQUIREMENT R08 — INVALID STATE HANDLING

The solver and validation layer must detect invalid puzzle states before attempting search.

Invalid states include states that fail structural or content validation. Examples may include:

- Wrong number of cells for the selected board size.
- Missing numbered tiles.
- Duplicate numbered tiles.
- Missing blank.
- More than one blank.
- Tile values outside the expected range.
- Board dimension inconsistent with the number of cells.
- Non-integer numbered tile values if integer tiles are required by the final representation.

The future implementation must define how invalid states are reported.

Invalid-state reporting decision:

- Core puzzle-state construction and validation may raise a controlled `InvalidPuzzleStateError` when malformed input is detected.
- Search entry points must not allow malformed boards to enter BFS or A*.
- Solver functions must return a structured search result with status `invalid` and a useful diagnostic message when the input board is malformed.
- Future web endpoints must translate invalid-state diagnostics into safe user-facing error responses.

## 16. Unsolvable-State Handling

ASSIGNMENT REQUIREMENT R09 — UNSOLVABLE STATE HANDLING

The solver must detect unsolvable puzzle states and avoid presenting them as solvable.

Requirements:

- Playable puzzles should be generated in a way that guarantees solvability, preferably by beginning from the goal state and applying legal randomized moves.
- Solver input validation must distinguish valid-but-unsolvable states from structurally invalid states.
- Unsolvable states must be reported clearly.
- Verification must include an invalid or unsolvable puzzle case.

The future implementation must document the selected solvability test for odd-width and even-width boards if solver generalization beyond 3x3 is implemented.

Unsolvable-state reporting decision:

- Structurally valid but unsolvable boards must be reported through a structured search result with status `unsolvable`.
- Unsolvable boards must not be searched exhaustively after the parity check determines they cannot reach the lower-right blank goal.
- Playable generated boards must be produced by legal scrambling from the goal so they are solvable by construction.

## 17. Search Result Structure

ASSIGNMENT REQUIREMENTS R17, R18, AND R19 — SEARCH RESULT STRUCTURE

The solver must return enough information to support grading, debugging, and optional GUI display.

The Python solver result must be a structured dataclass-style object named `SearchResult` or an equivalent clearly documented dataclass-compatible structure. It must include:

- Whether the search succeeded.
- Whether the input was invalid.
- Whether the input was unsolvable.
- Algorithm name.
- Start state.
- Goal state.
- Returned move sequence.
- Solution length.
- Expanded-state count.
- Optional final board path or state sequence if selected later.
- Optional error message or reason if search does not produce a solution.

The result fields must make the move sequence directly inspectable and must make `solution_length` equal to the number of moves in the returned sequence when solved.

## 18. Solution Move Inspection

The project must provide a way to display or inspect the returned move sequence.

Acceptable future options may include:

- Printing moves in the verification script.
- Returning moves from solver functions for inspection.
- Displaying moves in the web interface.
- Writing moves to a report-like output.

At minimum, the runnable verification artifact must print or otherwise display the returned move sequence in order. Any future GUI solver presentation may use a readable move list or step-through display, but it must preserve the documented blank-movement names exactly.

## 19. Expanded-State Counting Definition

The solver must track the number of expanded states for BFS and both A* variants.

ASSIGNMENT REQUIREMENT R19 — EXPANDED STATES

A state is counted as expanded when:

1. It is removed or popped from the search frontier for processing, and
2. The search algorithm proceeds to generate or examine its successors.

The goal state must not be counted as expanded if it is popped and immediately recognized as the goal before successor generation.

This exact expanded-state definition must be used consistently for BFS, A* with misplaced tiles, and A* with Manhattan distance.

## 20. Required Verification Cases

The runnable verification file must test:

- An already solved puzzle.
- A puzzle one move from the goal.
- A puzzle several moves from the goal.
- An invalid or unsolvable puzzle.

The verification must exercise:

- BFS.
- A* with misplaced-tiles heuristic.
- A* with Manhattan-distance heuristic.

Exact final verification boards may be deliberately selected when `03_verify_solver.py` is created. The several-moves-from-goal case should be reasonable for 3x3 BFS and must be documented in the verification file and test evidence.

## 21. Required Algorithm Comparison

The verification output must compare:

- BFS.
- A* with misplaced-tiles heuristic.
- A* with Manhattan-distance heuristic.

For each required algorithm and each applicable valid solvable case, the verification output must report:

- Solution length.
- Expanded states.
- Move sequence, or another explicit way to inspect the move sequence.

The comparison must make it possible to evaluate whether BFS returns minimum-move solutions on tested 3x3 cases and whether the A* heuristics produce correct goal-reaching solutions.

## 22. Web Application Requirements

The future web application must provide:

- A graphical browser interface.
- A Python-backed web service.
- Playable 3x3, 4x4, and 5x5 puzzle modes.
- Shared generalized puzzle architecture across sizes.
- Puzzle generation that guarantees solvability.
- Username-associated completion records.
- Persistent completion storage.
- A visual puzzle board that dominates the main screen.
- A persistent left sidebar.
- Difficulty controls for Easy, Medium, and Hard.
- Move counter.
- Running timer.
- "Did You Know..." fact area in the left sidebar.
- Fun fact rotation every 30 seconds.
- Completion confetti.
- Completion sound.
- Invalid-move animation and error sound.

Web architecture decision:

- Python web framework: FastAPI.
- ASGI server: Uvicorn for local development and Render startup.
- Frontend approach: server-served vanilla HTML, CSS, and JavaScript under `web/static/`.
- Rationale: FastAPI provides a small, well-supported Python web-service layer with clean JSON endpoints, straightforward static-file serving, simple Render deployment through an ASGI startup command, and no unnecessary frontend build pipeline for this assignment-sized application.

The web application must keep two modes clearly separated:

- GAME MODE: manual 3x3, 4x4, and 5x5 play using generalized puzzle-state logic and solvable legal scrambles.
- ASSIGNMENT SOLVER MODE: reviewer-facing solver demonstrations on reasonable fixed 3x3 cases only. The web UI must not advertise unrestricted 4x4 or 5x5 BFS/A* solving.

## 23. GUI Interaction Requirements

The GUI must support:

- Click or tap tile movement.
- Drag-style tile interaction.
- Invalid move feedback.
- Successful completion feedback.

Valid interaction behavior:

- If a user selects or drags a tile adjacent to the blank, the move is accepted.
- The tile moves into the blank.
- The board state updates.
- The move counter increments by one.
- The completion condition is checked.

Invalid interaction behavior:

- If a user selects or drags a tile that cannot legally move into the blank, the move is rejected.
- The tile shakes.
- The tile receives a temporary red tint or glow.
- The tile returns to its original position.
- A short buzz or error sound plays.
- The move counter does not increment.
- The timer continues unless the puzzle was already complete.

Exact drag threshold and fine input interaction details may be finalized during frontend implementation. The required behavior is that legal moves are orthogonal blank-adjacent swaps, while illegal moves preserve state and do not increment the move counter.

## 24. Visual Requirements

The visual direction must be:

- Dark.
- Polished.
- Pleasant.
- Larger and more visually prominent than the example sliding puzzle site referenced by the user.

The palette should use:

- Blacks.
- Charcoal greys.
- Greys.
- Muted purples.
- Brighter purple accents.

Layout requirements:

- The puzzle must dominate the main screen.
- The left sidebar must be persistent.
- Difficulty controls must be visible and usable.
- The move counter and timer must be visible.
- The "Did You Know..." fact area must be placed in the left sidebar.
- The axe decal must appear visually in the blank position.

The axe decal is decorative only and must not affect puzzle logic.

The exact axe decal asset may be selected during frontend implementation. The asset must be project-owned, license-safe, or otherwise safe to include, and it remains decorative only.

## 25. Timer and Move Counter

Timer requirements:

- The timer starts when a playable puzzle begins, or at another explicitly selected start event.
- The timer runs while the puzzle is active.
- The timer stops when the puzzle is successfully completed.
- The completion time is associated with the username and persisted.

Move counter requirements:

- The counter begins at zero for a new puzzle.
- Each valid manual move increments the counter by one.
- Invalid manual moves do not increment the counter.
- Solver-internal moves must not be confused with manual GUI move counts unless explicitly displayed separately.

Timer implementation decision:

- Timer starts when a new playable puzzle is generated.
- Timer displays whole elapsed seconds.
- Timer resets for each new puzzle or difficulty change.
- Timer stops when the puzzle is successfully completed and preserves the final displayed time.

## 26. Username and Persistence Requirements

The implementation must associate puzzle completion records with a username.

Completion records include:

- Username.
- Board size or difficulty.
- Completion duration/time in whole seconds.
- Move count.
- Server-side UTC completion timestamp.

Username and persistence implementation decisions:

- Identity model: simple username-only entry/display, not full authentication.
- The browser may retain the latest entered username locally for convenience.
- Persistence technology: SQLite through Python's standard `sqlite3` library.
- Database location is configured with the `PUZZLE_COMPLETIONS_DB` environment variable.
- Local development fallback database path is `data/completions.sqlite3`.
- Render deployment should set `PUZZLE_COMPLETIONS_DB` to a path on a mounted persistent disk, such as `/var/data/completions.sqlite3`.
- Completion submissions are validated server-side before insertion.
- Public leaderboard remains out of scope unless separately requested.

## 27. Deployment Requirements

The project will eventually be pushed to GitHub and deployed to Render as a web service.

The future implementation should be structured so that deployment to Render is practical. This may require:

- A clear Python web entry point.
- Dependency declaration.
- Environment-variable support for database or persistent storage.
- Static asset handling.
- Production-compatible startup command.

Exact Render deployment configuration may be finalized during deployment preparation after the web framework and persistence choices are selected.

## 28. Explicit Non-Requirements / Computational Limits

The project must not claim or imply:

- BFS can efficiently solve arbitrary 4x4 puzzles.
- BFS can efficiently solve arbitrary 5x5 puzzles.
- The graded solver evidence covers every possible 4x4 or 5x5 state.
- The axe decal is part of puzzle logic.
- The blank contributes to heuristic values.

Explicit limits:

- Required algorithm correctness and performance evidence is focused on reasonable 3x3 cases.
- The playable game must support 3x3, 4x4, and 5x5 boards.
- Board dimensions other than 3x3, 4x4, and 5x5 are outside scope.
- Arbitrary large-board optimal search is outside scope.

## 29. Requirements Traceability Table

| Requirement | Specification Coverage |
|---|---|
| R01. Write an LLM specification before asking for code. | This file is the pre-implementation specification artifact. |
| R02. Build a Python 3x3 sliding-tile puzzle solver. | Sections 1, 2, 10, 20, and 21. |
| R03. Design the solver so adapting it to 4x4 is straightforward. | Sections 6, 10, and 28. |
| R04. Choose and document one goal state. | Section 5 documents the lower-right blank goal state as ascending numbered tiles followed by `0`. |
| R05. Choose and document the board representation. | Section 7 documents an immutable flat Python tuple of integers with `N*N` entries. |
| R06. Choose and document move names. | Section 9 documents `UP`, `DOWN`, `LEFT`, and `RIGHT` as blank-movement directions. |
| R07. Choose and document A* tie-breaking behavior. | Section 14 documents deterministic ordering by lowest `f`, then lowest `h`, then earliest insertion order. |
| R08. Handle invalid puzzle states. | Section 15. |
| R09. Handle unsolvable puzzle states. | Section 16. |
| R10. Implement breadth-first search. | Sections 10 and 11. |
| R11. BFS must find a minimum-move solution for tested 3x3 puzzle states. | Section 11. |
| R12. Implement A* with the misplaced-tiles heuristic. | Sections 10 and 12. |
| R13. Implement A* with the Manhattan-distance heuristic. | Sections 10 and 13. |
| R14. Misplaced tiles must ignore the blank. | Section 12. |
| R15. Manhattan distance must ignore the blank. | Section 13. |
| R16. Both heuristics must equal zero at the goal. | Sections 12 and 13. |
| R17. Provide a way to display or inspect the returned move sequence. | Section 18. |
| R18. Track solution length. | Sections 10, 17, and 21. |
| R19. Track number of expanded states. | Sections 10, 17, 19, and 21. Section 19 defines expansion as successor generation after frontier removal. |
| R20. Create a runnable test/verification file. | Sections 2, 20, and 21. |
| R21. Test an already solved puzzle. | Section 20. |
| R22. Test a puzzle one move from the goal. | Section 20. |
| R23. Test a puzzle several moves from the goal. | Section 20. |
| R24. Test an invalid or unsolvable puzzle. | Sections 15, 16, and 20. |
| R25. Compare BFS, A* misplaced, and A* Manhattan. | Section 21. |
| R26. Report solution length for all three algorithms. | Section 21. |
| R27. Report expanded states for all three algorithms. | Section 21. |
| R28. Submit the Python solver. | Section 2. |
| R29. Submit the runnable test/verification script. | Section 2. |
| R30. Submit the original LLM specification. | Section 2 and this file itself. |
| R31. Submit test evidence/results. | Sections 2, 20, and 21. |

## 30. User Decisions Required

The following core Python solver decisions have been resolved and no longer block solver implementation:

- RESOLVED: Exact Python board representation is an immutable flat Python tuple of integers with `N*N` entries.
- RESOLVED: Internal blank value is integer `0`.
- RESOLVED: Move names are `UP`, `DOWN`, `LEFT`, and `RIGHT`.
- RESOLVED: Move directions describe blank movement.
- RESOLVED: A* tie-breaking is lowest `f`, then lowest `h`, then earliest insertion order.
- RESOLVED: Expanded-state counting increments only when a popped frontier state proceeds to successor generation; a popped goal is not counted if recognized before successor generation.
- RESOLVED: Invalid malformed boards are rejected through controlled validation behavior and reported by solver entry points as status `invalid`.
- RESOLVED: Structurally valid unsolvable boards are reported by solver entry points as status `unsolvable` after solvability checking.
- RESOLVED: Solver results use a structured dataclass-style result object with inspectable move sequence, solution length, expanded-state count, status, and diagnostic fields.

The following later-stage implementation choices remain pending. They must be made before the relevant implementation stage begins, but they do not block implementation of the core Python puzzle solver:

- RESOLVED: Python web framework is FastAPI with Uvicorn.
- RESOLVED: Persistence technology is SQLite through Python's standard `sqlite3` library.
- RESOLVED: Identity model is username-only entry/display, not full authentication.
- RESOLVED: Timer starts when a new playable puzzle is generated and displays whole seconds.
- Future verification decision pending: Exact final verification boards.
- Future optional GUI decision pending: Solver-result GUI presentation style.
- Future test decision pending: Whether to add a formal test framework in addition to the direct runnable verification script.
- Future frontend decision pending: Exact drag threshold and detailed input handling.
- Future asset decision pending: Exact axe decal and audio assets.
- RESOLVED: Completion records store username, board size, duration in seconds, move count, and server-side UTC completion timestamp.
- Future product decision pending: Whether a leaderboard is desired. It is not required by default.
- Future deployment decision pending: Exact Render deployment configuration.

## 31. Implementation Authorization Checklist

Core Python solver implementation is now authorized to begin.

Before core Python solver implementation begins, confirm that:

- This specification has been reviewed.
- The exact board representation has been selected.
- The exact blank value has been selected.
- The exact move naming convention has been selected.
- The exact A* tie-breaking rule has been selected.
- The exact expanded-state counting rule has been selected.
- The selected lower-right blank goal has been retained.
- The user has explicitly authorized core Python solver implementation to begin.

The core Python solver may be implemented before the web-application decisions are resolved.

Before final verification-script and test-evidence work begins, confirm that:

- The exact verification boards have been selected or explicitly approved.
- The testing framework has been selected or an approved direct runnable verification script approach has been confirmed.
- The direct verification script prints actual algorithm results rather than hypothetical values.

Before web-application implementation begins, confirm that:

- The Python web framework has been selected.
- The username and authentication approach has been selected.
- The timer behavior and precision have been selected.
- Frontend, audio, asset, and deployment decisions needed for that implementation stage have been resolved.

## IMPLEMENTATION MAY BEGIN ONLY AFTER THESE DECISIONS ARE RESOLVED.

Core Python solver implementation may now begin because the implementation-critical solver decisions in Section 30 have been resolved.

Final verification artifacts, web-application code, database files, frontend files, deployment files, and generated assets should not be created until their remaining user-controlled decisions are resolved and that implementation stage is explicitly authorized.
