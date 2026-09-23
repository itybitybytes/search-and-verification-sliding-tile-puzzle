"""SQLite persistence for username-associated completion records.

File purpose:
    Store completed puzzle results outside browser local state.

Deployment note:
    Set PUZZLE_COMPLETIONS_DB on Render to a path on a persistent disk, for
    example /var/data/completions.sqlite3. When unset, local development uses
    data/completions.sqlite3 inside the project directory.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Any


SUPPORTED_COMPLETION_SIZES = frozenset({3, 4, 5})
MAX_USERNAME_LENGTH = 32
MAX_DURATION_SECONDS = 24 * 60 * 60
MAX_MOVE_COUNT = 100_000

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = BASE_DIR / "data" / "completions.sqlite3"
DATABASE_ENV_VAR = "PUZZLE_COMPLETIONS_DB"


class CompletionValidationError(ValueError):
    """Raised when client-submitted completion data fails server validation."""


@dataclass(frozen=True)
class CompletionRecord:
    id: int
    username: str
    board_size: int
    duration_seconds: int
    move_count: int
    completed_at: str

    def as_dict(self) -> dict[str, int | str]:
        return {
            "id": self.id,
            "username": self.username,
            "board_size": self.board_size,
            "duration_seconds": self.duration_seconds,
            "move_count": self.move_count,
            "completed_at": self.completed_at,
        }


def database_path() -> Path:
    configured = os.environ.get(DATABASE_ENV_VAR)
    if configured:
        return Path(configured)
    return DEFAULT_DATABASE_PATH


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_completion_store(db_path: Path | None = None) -> None:
    """Create the completion schema if it does not already exist."""

    with closing(_connect(db_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    board_size INTEGER NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    move_count INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    CHECK (board_size IN (3, 4, 5)),
                    CHECK (duration_seconds >= 0),
                    CHECK (move_count >= 0)
                )
                """
            )


def _validated_int(value: Any, field_name: str, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CompletionValidationError(f"{field_name} must be an integer.")
    if value < 0:
        raise CompletionValidationError(f"{field_name} must be nonnegative.")
    if maximum is not None and value > maximum:
        raise CompletionValidationError(f"{field_name} is too large.")
    return value


def validate_completion_data(
    username: str,
    board_size: int,
    duration_seconds: int,
    move_count: int,
) -> tuple[str, int, int, int]:
    """Validate a completion submission before inserting it into storage."""

    normalized_username = username.strip()
    if not normalized_username:
        raise CompletionValidationError("username must be nonempty.")
    if len(normalized_username) > MAX_USERNAME_LENGTH:
        raise CompletionValidationError(
            f"username must be {MAX_USERNAME_LENGTH} characters or fewer."
        )

    validated_board_size = _validated_int(board_size, "board_size")
    if validated_board_size not in SUPPORTED_COMPLETION_SIZES:
        supported = ", ".join(str(size) for size in sorted(SUPPORTED_COMPLETION_SIZES))
        raise CompletionValidationError(f"board_size must be one of: {supported}.")

    validated_duration = _validated_int(
        duration_seconds,
        "duration_seconds",
        MAX_DURATION_SECONDS,
    )
    validated_moves = _validated_int(move_count, "move_count", MAX_MOVE_COUNT)
    return normalized_username, validated_board_size, validated_duration, validated_moves


def create_completion_record(
    username: str,
    board_size: int,
    duration_seconds: int,
    move_count: int,
    db_path: Path | None = None,
) -> CompletionRecord:
    """Persist one validated puzzle completion record."""

    normalized_username, validated_size, validated_duration, validated_moves = (
        validate_completion_data(username, board_size, duration_seconds, move_count)
    )
    completed_at = (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )

    initialize_completion_store(db_path)
    with closing(_connect(db_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO completions (
                    username,
                    board_size,
                    duration_seconds,
                    move_count,
                    completed_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    normalized_username,
                    validated_size,
                    validated_duration,
                    validated_moves,
                    completed_at,
                ),
            )
            record_id = int(cursor.lastrowid)

    return CompletionRecord(
        id=record_id,
        username=normalized_username,
        board_size=validated_size,
        duration_seconds=validated_duration,
        move_count=validated_moves,
        completed_at=completed_at,
    )


def list_completion_records(db_path: Path | None = None) -> list[CompletionRecord]:
    """Read persisted completion records using a fresh database connection."""

    initialize_completion_store(db_path)
    with closing(_connect(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT id, username, board_size, duration_seconds, move_count, completed_at
            FROM completions
            ORDER BY id
            """
        ).fetchall()

    return [
        CompletionRecord(
            id=int(row["id"]),
            username=str(row["username"]),
            board_size=int(row["board_size"]),
            duration_seconds=int(row["duration_seconds"]),
            move_count=int(row["move_count"]),
            completed_at=str(row["completed_at"]),
        )
        for row in rows
    ]
