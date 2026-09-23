from __future__ import annotations

import importlib.util
import io
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from puzzle import PuzzleState


def load_cli_module() -> ModuleType:
    cli_path = Path(__file__).resolve().parents[1] / "06_cli_game.py"
    spec = importlib.util.spec_from_file_location("cli_game_for_tests", cli_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load CLI module from {cli_path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CliHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cli = load_cli_module()

    def test_normalize_command_trims_and_uppercases_input(self) -> None:
        self.assertEqual(self.cli.normalize_command("  left  "), "LEFT")
        self.assertEqual(self.cli.normalize_command("\tHelp\n"), "HELP")

    def test_comparison_state_is_fixed_reasonable_3x3_state(self) -> None:
        self.assertEqual(
            self.cli.comparison_state_3x3(),
            (1, 2, 3, 7, 0, 6, 5, 4, 8),
        )

    def test_ascii_fallback_uses_plain_dash_and_ascii_blank(self) -> None:
        with patch.dict(os.environ, {"PUZZLE_ASCII": "1"}):
            self.assertFalse(self.cli.supports_unicode())
            self.assertEqual(self.cli.display_dash(), "-")
            rendered = PuzzleState.goal(3).render(use_unicode_blank=self.cli.supports_unicode())
            self.assertIn("__", rendered)

    def test_render_game_screen_keeps_metrics_and_fact_readable(self) -> None:
        with patch.dict(os.environ, {"PUZZLE_ASCII": "1"}):
            output = io.StringIO()
            with redirect_stdout(output):
                self.cli.render_game_screen(
                    username="tester",
                    difficulty="Easy",
                    state=PuzzleState.goal(3),
                    moves=2,
                    elapsed_seconds=30,
                    message="[INVALID MOVE] Example.",
                )

        text = output.getvalue()
        self.assertIn("USERNAME: tester", text)
        self.assertIn("DIFFICULTY: EASY - 3x3", text)
        self.assertIn("MOVES: 2", text)
        self.assertIn("TIME: 0:30", text)
        self.assertIn("DID YOU KNOW?", text)
        self.assertIn("PUZZLE BOARD", text)
        self.assertIn("__", text)
        self.assertIn("[INVALID MOVE] Example.", text)

    def test_save_completion_prints_success_banner_without_real_record_file(self) -> None:
        fake_record = {"completed_at": "2026-09-03T00:00:00+00:00"}
        with patch.object(self.cli, "append_record", return_value=fake_record) as append:
            with patch.dict(os.environ, {"PUZZLE_ASCII": "1"}):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.cli.save_completion("tester", "Easy", 3, 6, 125)

        text = output.getvalue()
        self.assertIn("PUZZLE COMPLETE", text)
        self.assertIn("Final moves: 6", text)
        self.assertIn("Final time: 2:05", text)
        self.assertIn("Saved completion record", text)
        append.assert_called_once_with(
            username="tester",
            difficulty="Easy",
            board_size=3,
            moves=6,
            elapsed_seconds=125,
        )


if __name__ == "__main__":
    unittest.main()
