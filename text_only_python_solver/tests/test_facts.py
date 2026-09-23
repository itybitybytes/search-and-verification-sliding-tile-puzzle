from __future__ import annotations

import unittest

from puzzle import FACTS, FACT_ROTATION_SECONDS, current_fact, fact_index_for_elapsed


class FactRotationTests(unittest.TestCase):
    def test_rotation_interval_is_thirty_seconds(self) -> None:
        self.assertEqual(FACT_ROTATION_SECONDS, 30)

    def test_fact_index_rotates_by_elapsed_time_without_threads(self) -> None:
        facts = ("first", "second", "third")
        expected = {
            0: 0,
            29: 0,
            30: 1,
            59: 1,
            60: 2,
        }
        for elapsed, index in expected.items():
            with self.subTest(elapsed=elapsed):
                self.assertEqual(fact_index_for_elapsed(elapsed, facts), index)
                self.assertEqual(current_fact(elapsed, facts), facts[index])

    def test_default_facts_cover_required_topics(self) -> None:
        joined = " ".join(FACTS).lower()
        for keyword in (
            "sliding",
            "breadth-first",
            "a*",
            "manhattan",
            "misplaced",
            "heuristic",
            "state space",
            "optimal",
        ):
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, joined)

    def test_fact_rotation_rejects_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            fact_index_for_elapsed(-1)
        with self.assertRaises(ValueError):
            fact_index_for_elapsed(0, ())
        with self.assertRaises(ValueError):
            fact_index_for_elapsed(0, ("only",), rotation_seconds=0)


if __name__ == "__main__":
    unittest.main()
