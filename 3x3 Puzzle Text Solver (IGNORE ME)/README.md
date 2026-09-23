# 3x3 Puzzle Text Solver

Separate text-only Python subproject for the sliding-tile puzzle solver.

This folder is intentionally separate from `FastAPI 3x3 Puzzle/`. It is meant for console/text usage and does not include the browser GUI, FastAPI backend, persistence layer, sounds, confetti, or Render web deployment files.

## Contents

- `02_python_solver.py` — reviewer-facing Python solver facade.
- `03_verify_solver.py` — direct verification script.
- `04_TEST_EVIDENCE.md` — verification evidence copied from the verified solver run.
- `01_LLM_SPECIFICATION.md` — solver requirements and implementation decisions.
- `05_REQUIREMENTS_TRACEABILITY.md` — requirement mapping for the broader project.
- `solver/` — reusable puzzle model, validation, solvability, BFS, A* misplaced, A* Manhattan, heuristics, and fixed verification cases.

## Run

```bash
python 02_python_solver.py
python 03_verify_solver.py
```

No third-party Python packages are required for the text-only solver.
