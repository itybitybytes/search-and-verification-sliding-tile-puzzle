"""Backend smoke tests for the FastAPI web application."""

from __future__ import annotations

import os
from pathlib import Path
import unittest

from fastapi.testclient import TestClient

from solver import is_solvable
from web.app import app
from web.persistence import DATABASE_ENV_VAR, list_completion_records

TEST_DATA_DIR = Path("test_data")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class WebApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_main_page_serves_gui_shell(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sliding Tile Puzzle", response.text)
        self.assertIn("DID YOU KNOW", response.text)
        self.assertIn("3x3 Solver Demonstration", response.text)
        self.assertIn("solver-comparison-body", response.text)
        self.assertIn("solver-playback-board", response.text)
        self.assertIn("Required search verification focuses on fixed reasonable 3x3 states.", response.text)

    def test_config_documents_supported_difficulties_and_modes(self) -> None:
        response = self.client.get("/api/config")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            [(item["key"], item["size"]) for item in payload["difficulties"]],
            [("easy", 3), ("medium", 4), ("hard", 5)],
        )
        self.assertIn("3x3", payload["game_mode"])
        self.assertIn("3x3", payload["solver_mode"])
        self.assertEqual(payload["username"]["mode"], "username-only")
        self.assertEqual(payload["persistence"]["database"], "SQLite")
        self.assertEqual(payload["persistence"]["database_env_var"], DATABASE_ENV_VAR)
        self.assertFalse(payload["persistence"]["public_leaderboard"])

    def test_config_serves_sidebar_fact_content(self) -> None:
        response = self.client.get("/api/config")

        self.assertEqual(response.status_code, 200)
        facts = response.json()["facts"]
        self.assertGreaterEqual(len(facts), 8)
        self.assertTrue(all(isinstance(fact, str) and fact for fact in facts))
        self.assertTrue(all(len(fact) <= 100 for fact in facts))
        self.assertTrue(
            any("A*" in fact or "Breadth-first" in fact or "Manhattan" in fact for fact in facts)
        )

    def test_new_puzzle_generates_solvable_supported_sizes(self) -> None:
        expected_sizes = {"easy": 3, "medium": 4, "hard": 5}

        for difficulty, size in expected_sizes.items():
            with self.subTest(difficulty=difficulty):
                response = self.client.get(f"/api/new-puzzle?difficulty={difficulty}&seed=7")
                self.assertEqual(response.status_code, 200)
                payload = response.json()

                self.assertEqual(payload["mode"], "GAME MODE")
                self.assertEqual(payload["state"]["size"], size)
                self.assertEqual(len(payload["state"]["tiles"]), size * size)
                self.assertTrue(is_solvable(tuple(payload["state"]["tiles"]), size))

    def test_new_puzzle_rejects_unsupported_difficulty(self) -> None:
        response = self.client.get("/api/new-puzzle?difficulty=expert")

        self.assertEqual(response.status_code, 422)

    def test_solver_demo_is_limited_to_fixed_3x3_cases(self) -> None:
        response = self.client.get("/api/solver-demo?case=comparison")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "ASSIGNMENT SOLVER MODE")
        self.assertEqual(payload["state"]["size"], 3)
        self.assertEqual(
            [result["algorithm"] for result in payload["results"]],
            ["BFS", "A* Misplaced", "A* Manhattan"],
        )
        self.assertEqual({result["solution_length"] for result in payload["results"]}, {6})
        for result in payload["results"]:
            self.assertTrue(result["solved"])
            self.assertEqual(result["solution_length"], len(result["moves"]))
            self.assertIsInstance(result["expanded_states"], int)
            self.assertGreaterEqual(result["expanded_states"], 0)

    def test_solver_demo_rejects_unapproved_cases(self) -> None:
        response = self.client.get("/api/solver-demo?case=custom")

        self.assertEqual(response.status_code, 422)

    def test_completion_endpoint_persists_valid_records(self) -> None:
        previous_db_path = os.environ.get(DATABASE_ENV_VAR)
        TEST_DATA_DIR.mkdir(exist_ok=True)
        db_path = TEST_DATA_DIR / "endpoint-valid.sqlite3"
        db_path.unlink(missing_ok=True)
        os.environ[DATABASE_ENV_VAR] = str(db_path)
        try:
            submissions = (
                {"username": "Ada", "board_size": 3, "duration_seconds": 17, "move_count": 9},
                {"username": "Grace", "board_size": 4, "duration_seconds": 61, "move_count": 22},
                {"username": "Ada", "board_size": 5, "duration_seconds": 94, "move_count": 30},
            )

            for submission in submissions:
                response = self.client.post("/api/completions", json=submission)
                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertTrue(payload["saved"])
                self.assertEqual(payload["record"]["username"], submission["username"])
                self.assertEqual(payload["record"]["board_size"], submission["board_size"])
                self.assertEqual(payload["record"]["duration_seconds"], submission["duration_seconds"])
                self.assertEqual(payload["record"]["move_count"], submission["move_count"])
                self.assertTrue(payload["record"]["completed_at"].endswith("Z"))

            records = list_completion_records(db_path)
            self.assertEqual(len(records), 3)
            self.assertEqual([record.username for record in records], ["Ada", "Grace", "Ada"])
            self.assertEqual([record.board_size for record in records], [3, 4, 5])
        finally:
            if previous_db_path is None:
                os.environ.pop(DATABASE_ENV_VAR, None)
            else:
                os.environ[DATABASE_ENV_VAR] = previous_db_path

    def test_completion_endpoint_rejects_bad_submissions(self) -> None:
        previous_db_path = os.environ.get(DATABASE_ENV_VAR)
        TEST_DATA_DIR.mkdir(exist_ok=True)
        db_path = TEST_DATA_DIR / "endpoint-invalid.sqlite3"
        db_path.unlink(missing_ok=True)
        os.environ[DATABASE_ENV_VAR] = str(db_path)
        try:
            bad_submissions = (
                {"username": "", "board_size": 3, "duration_seconds": 1, "move_count": 1},
                {"username": "Ada", "board_size": 6, "duration_seconds": 1, "move_count": 1},
                {"username": "Ada", "board_size": 3, "duration_seconds": -1, "move_count": 1},
                {"username": "Ada", "board_size": 3, "duration_seconds": 1, "move_count": -1},
                {
                    "username": "Ada",
                    "board_size": 3,
                    "duration_seconds": 1,
                    "move_count": 1,
                    "admin": True,
                },
            )

            for submission in bad_submissions:
                with self.subTest(submission=submission):
                    response = self.client.post("/api/completions", json=submission)
                    self.assertIn(response.status_code, {400, 422})
        finally:
            if previous_db_path is None:
                os.environ.pop(DATABASE_ENV_VAR, None)
            else:
                os.environ[DATABASE_ENV_VAR] = previous_db_path

    def test_deployment_files_document_render_startup(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        render_config = (PROJECT_ROOT / "render.yaml").read_text(encoding="utf-8")
        requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

        for required_file in (
            "01_LLM_SPECIFICATION.md",
            "02_python_solver.py",
            "03_verify_solver.py",
            "04_TEST_EVIDENCE.md",
            "05_REQUIREMENTS_TRACEABILITY.md",
        ):
            self.assertIn(required_file, readme)

        self.assertIn("fastapi", requirements)
        self.assertIn("uvicorn[standard]", requirements)
        self.assertIn("startCommand: uvicorn web.app:app --host 0.0.0.0 --port $PORT", render_config)
        self.assertIn("PUZZLE_COMPLETIONS_DB", render_config)
        self.assertIn("/var/data/completions.sqlite3", render_config)
        self.assertIn("PUZZLE_COMPLETIONS_DB", readme)
        self.assertIn("DATABASE_URL", readme)
        self.assertIn(".env", gitignore)
        self.assertIn("__pycache__/", gitignore)
        self.assertIn("data/", gitignore)


if __name__ == "__main__":
    unittest.main()
