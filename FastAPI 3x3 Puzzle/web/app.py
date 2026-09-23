"""FastAPI entry point for the playable sliding-tile web application.

File purpose:
    Serve the browser GUI, generate playable solvable puzzles, and expose
    restricted 3x3 assignment solver demonstrations for reviewers.

Architecture decision:
    FastAPI is used as a small Python web-service layer for local development,
    GitHub source control, and Render deployment.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .facts import SIDEBAR_FACTS
from .game_service import difficulty_payload, generate_playable_puzzle, solver_demo
from .persistence import (
    DATABASE_ENV_VAR,
    CompletionValidationError,
    create_completion_record,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Sliding Tile Puzzle", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CompletionSubmission(BaseModel):
    username: str
    board_size: int
    duration_seconds: int
    move_count: int

    class Config:
        extra = "forbid"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict[str, object]:
    return {
        "difficulties": difficulty_payload(),
        "default_difficulty": "easy",
        "timer": {"starts": "new puzzle", "precision": "seconds"},
        "username": {"mode": "username-only", "authentication": "not required"},
        "persistence": {
            "database": "SQLite",
            "database_env_var": DATABASE_ENV_VAR,
            "public_leaderboard": False,
        },
        "game_mode": "Manual play supports Easy 3x3, Medium 4x4, and Hard 5x5.",
        "solver_mode": "Assignment solver demonstrations are limited to fixed reasonable 3x3 cases.",
        "facts": list(SIDEBAR_FACTS),
    }


@app.get("/api/new-puzzle")
def new_puzzle(
    difficulty: str = Query("easy", pattern="^(easy|medium|hard)$"),
    seed: int | None = None,
) -> dict[str, object]:
    try:
        return generate_playable_puzzle(difficulty, seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/solver-demo")
def solver_demo_endpoint(case: str = Query("comparison", pattern="^(solved|several|comparison)$")) -> dict[str, object]:
    try:
        return solver_demo(case)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/completions")
def save_completion(submission: CompletionSubmission) -> dict[str, object]:
    try:
        record = create_completion_record(
            username=submission.username,
            board_size=submission.board_size,
            duration_seconds=submission.duration_seconds,
            move_count=submission.move_count,
        )
    except CompletionValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"saved": True, "record": record.as_dict()}
