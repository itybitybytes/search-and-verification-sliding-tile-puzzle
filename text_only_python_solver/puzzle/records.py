"""Local JSON completion records for the text-only support systems.

File purpose:
    Store and retrieve username-associated puzzle completion records without a
    database, server, SQL, or network dependency.

Runtime file:
    `completion_records.json` at the text-only subproject root.

Graded submission artifact:
    Supporting implementation file for the text-only Python solver subproject.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .generator import DIFFICULTY_SIZES
from .validation import SUPPORTED_SIZES

DEFAULT_RECORDS_PATH = Path(__file__).resolve().parents[1] / "completion_records.json"


def format_elapsed_time(elapsed_seconds: int) -> str:
    """Format nonnegative elapsed seconds as M:SS or H:MM:SS."""

    if isinstance(elapsed_seconds, bool) or not isinstance(elapsed_seconds, int):
        raise ValueError("elapsed_seconds must be a nonnegative integer.")
    if elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be nonnegative.")

    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _validate_nonnegative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be a nonnegative integer.")
    if value < 0:
        raise ValueError(f"{field_name} must be nonnegative.")
    return value


def validate_completion_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one completion record."""

    username = str(record.get("username", "")).strip()
    if not username:
        raise ValueError("username must be nonempty.")
    if len(username) > 40:
        raise ValueError("username must be 40 characters or fewer.")

    board_size = _validate_nonnegative_int(record.get("board_size"), "board_size")
    if board_size not in SUPPORTED_SIZES:
        raise ValueError("board_size must be one of 3, 4, or 5.")

    difficulty = str(record.get("difficulty", "")).strip()
    if difficulty not in DIFFICULTY_SIZES:
        expected = ", ".join(DIFFICULTY_SIZES)
        raise ValueError(f"difficulty must be one of {expected}.")
    if DIFFICULTY_SIZES[difficulty] != board_size:
        raise ValueError("difficulty does not match board_size.")

    moves = _validate_nonnegative_int(record.get("moves"), "moves")
    elapsed_seconds = _validate_nonnegative_int(
        record.get("elapsed_seconds"),
        "elapsed_seconds",
    )

    completed_at = str(record.get("completed_at", "")).strip()
    if not completed_at:
        raise ValueError("completed_at must be nonempty.")

    return {
        "username": username,
        "difficulty": difficulty,
        "board_size": board_size,
        "moves": moves,
        "elapsed_seconds": elapsed_seconds,
        "formatted_time": format_elapsed_time(elapsed_seconds),
        "completed_at": completed_at,
    }


def load_records(path: str | Path = DEFAULT_RECORDS_PATH) -> list[dict[str, Any]]:
    """Load records safely, treating missing/empty/malformed files as empty."""

    records_path = Path(path)
    try:
        raw_text = records_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    if not raw_text.strip():
        return []

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    valid_records = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        try:
            valid_records.append(validate_completion_record(item))
        except ValueError:
            continue
    return valid_records


def save_records(
    records: Iterable[dict[str, Any]],
    path: str | Path = DEFAULT_RECORDS_PATH,
) -> None:
    """Validate and save all records as JSON."""

    normalized = [validate_completion_record(record) for record in records]
    records_path = Path(path)
    records_path.parent.mkdir(parents=True, exist_ok=True)
    records_path.write_text(
        json.dumps(normalized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def append_record(
    username: str,
    difficulty: str,
    board_size: int,
    moves: int,
    elapsed_seconds: int,
    path: str | Path = DEFAULT_RECORDS_PATH,
) -> dict[str, Any]:
    """Append a validated completion record and return the saved record."""

    record = validate_completion_record(
        {
            "username": username,
            "difficulty": difficulty,
            "board_size": board_size,
            "moves": moves,
            "elapsed_seconds": elapsed_seconds,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    records = load_records(path)
    records.append(record)
    save_records(records, path)
    return record


def records_for_username(
    username: str,
    path: str | Path = DEFAULT_RECORDS_PATH,
) -> list[dict[str, Any]]:
    """Return saved completion records for an exact username match."""

    normalized_username = username.strip()
    return [
        record
        for record in load_records(path)
        if record["username"] == normalized_username
    ]
