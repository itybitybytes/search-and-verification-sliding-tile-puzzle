# 04 Test Evidence

Required top-level graded submission artifact.

This evidence was generated from the current implementation. The results below are copied from an actual run of the verification script; no algorithm metrics were invented or adjusted.

## Command Executed

```text
python 03_verify_solver.py
```

Result: all verification assertions passed.

## Solver Conventions

Goal state:

```text
1 2 3
4 5 6
7 8 _
```

Board representation: immutable flat Python tuple of integers with `N*N` entries.

Blank representation: integer `0` internally. The formatted evidence displays the blank as `_`.

Move semantics: `UP`, `DOWN`, `LEFT`, and `RIGHT` describe movement of the blank, not the numbered tile.

A* tie-breaking: lowest `f = g + h`, then lowest `h`, then earliest insertion order.

Expanded-state counting convention: a state is counted as expanded only after it is popped from the frontier and the algorithm proceeds to generate or examine successors. A popped goal state is not counted as expanded when it is immediately recognized as the goal.

## Test 1 — Solved Puzzle

Starting state:

```text
1 2 3
4 5 6
7 8 _
```

| Algorithm | Move Sequence | Solution Length | Expanded States |
|---|---|---:|---:|
| BFS | `(none)` | 0 | 0 |
| A* Misplaced | `(none)` | 0 | 0 |
| A* Manhattan | `(none)` | 0 | 0 |

Assertions verified: solved length is `0`, returned move sequence is empty, `solution_length == len(moves)`, and both heuristics return `0` at the goal.

## Test 2 — One Move From Goal

Starting state:

```text
1 2 3
4 5 6
7 _ 8
```

| Algorithm | Move Sequence | Solution Length | Expanded States |
|---|---|---:|---:|
| BFS | `RIGHT` | 1 | 3 |
| A* Misplaced | `RIGHT` | 1 | 1 |
| A* Manhattan | `RIGHT` | 1 | 1 |

Assertions verified: one-move solution length is `1`, returned moves are legal, returned moves reach the goal, and `solution_length == len(moves)`.

## Test 3 — Several Moves From Goal

Starting state:

```text
1 2 3
_ 4 6
7 5 8
```

| Algorithm | Move Sequence | Solution Length | Expanded States |
|---|---|---:|---:|
| BFS | `RIGHT, DOWN, RIGHT` | 3 | 16 |
| A* Misplaced | `RIGHT, DOWN, RIGHT` | 3 | 3 |
| A* Manhattan | `RIGHT, DOWN, RIGHT` | 3 | 3 |

Assertions verified: returned moves are legal, returned moves reach the goal, and `solution_length == len(moves)`.

## Test 4 — Invalid Puzzle

Starting state:

```text
1 2 3
4 5 6
7 7 _
```

| Algorithm | Status | Message |
|---|---|---|
| BFS | `invalid` | Board contains duplicate tile value(s): `[7]`. |
| A* Misplaced | `invalid` | Board contains duplicate tile value(s): `[7]`. |
| A* Manhattan | `invalid` | Board contains duplicate tile value(s): `[7]`. |

Assertions verified: invalid state is handled by all three algorithms, no solution moves are returned, solution length is `0`, and expanded states are `0`.

## Test 5 — Unsolvable Puzzle

Starting state:

```text
1 2 3
4 5 6
8 7 _
```

| Algorithm | Status | Message |
|---|---|---|
| BFS | `unsolvable` | Puzzle is structurally valid but unsolvable. |
| A* Misplaced | `unsolvable` | Puzzle is structurally valid but unsolvable. |
| A* Manhattan | `unsolvable` | Puzzle is structurally valid but unsolvable. |

Assertions verified: valid but unsolvable state is identified by all three algorithms, no exhaustive search is performed, no solution moves are returned, solution length is `0`, and expanded states are `0`.

## BFS vs A* Comparison

Comparison starting state:

```text
1 2 3
7 _ 6
5 4 8
```

| Algorithm | Solution Length | Expanded States |
|---|---:|---:|
| BFS | 6 | 90 |
| A* Misplaced | 6 | 8 |
| A* Manhattan | 6 | 6 |

Returned move sequences:

| Algorithm | Move Sequence |
|---|---|
| BFS | `DOWN, LEFT, UP, RIGHT, DOWN, RIGHT` |
| A* Misplaced | `DOWN, LEFT, UP, RIGHT, DOWN, RIGHT` |
| A* Manhattan | `DOWN, LEFT, UP, RIGHT, DOWN, RIGHT` |

Assertions verified: all three algorithms found a solution, all three returned the same optimal solution length on the comparison state, returned moves were legal, returned moves reached the goal, and `solution_length == len(moves)`.

Measured comparison note: in this run, A* Manhattan expanded fewer states than A* Misplaced and BFS. A* Misplaced expanded fewer states than BFS.

## Limitations

The required solver verification focuses on modest 3x3 states. The puzzle model is dimension-aware for supported 3x3, 4x4, and 5x5 boards, but this evidence does not claim BFS is practical for arbitrary 4x4 or 5x5 optimal solving.
