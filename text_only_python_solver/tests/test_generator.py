from __future__ import annotations

import random
import unittest

from puzzle import (
    DIFFICULTY_SIZES,
    PuzzleState,
    generate_puzzle,
    generate_puzzle_by_size,
    is_solvable,
)


class PuzzleGeneratorTests(unittest.TestCase):
    def test_generates_valid_solvable_non_goal_puzzles_for_difficulties(self) -> None:
        for index, (difficulty, size) in enumerate(DIFFICULTY_SIZES.items()):
            with self.subTest(difficulty=difficulty):
                state = generate_puzzle(difficulty, scramble_steps=12, rng=random.Random(index))
                self.assertIsInstance(state, PuzzleState)
                self.assertEqual(state.dimension, size)
                self.assertFalse(state.is_goal())
                self.assertTrue(is_solvable(state.board, size))
                self.assertEqual(set(state.board), set(range(size * size)))

    def test_generates_supported_sizes_without_size_specific_logic(self) -> None:
        for size in (3, 4, 5):
            with self.subTest(size=size):
                state = generate_puzzle_by_size(size, scramble_steps=10, rng=random.Random(size))
                self.assertEqual(state.dimension, size)
                self.assertEqual(len(state.board), size * size)
                self.assertFalse(state.is_goal())
                self.assertTrue(is_solvable(state.board, size))

    def test_rejects_unsupported_size_and_zero_scramble(self) -> None:
        with self.assertRaises(ValueError):
            generate_puzzle_by_size(6, rng=random.Random(1))
        with self.assertRaises(ValueError):
            generate_puzzle_by_size(3, scramble_steps=0, rng=random.Random(1))

    def test_rejects_unknown_difficulty(self) -> None:
        with self.assertRaises(ValueError):
            generate_puzzle("Extreme", rng=random.Random(1))


if __name__ == "__main__":
    unittest.main()
