from __future__ import annotations

from pathlib import Path
import unittest

from scripts.run_sol_sequential_revisits import (
    DEFAULT_PER_SUBJECT_SOL_SPEND_USD,
    SEQUENCE,
    _parser,
    _subject_command,
)


class SequentialRevisitRunnerTests(unittest.TestCase):
    def test_governed_sequence_contains_all_eleven_prior_tickers(self) -> None:
        self.assertEqual(
            SEQUENCE,
            ("AAPL", "AMD", "AMZN", "BA", "GOOGL", "JPM", "META", "MSFT", "NVDA", "TSLA", "XOM"),
        )

    def test_default_spend_ceiling_is_fifteen_dollars_per_subject(self) -> None:
        args = _parser().parse_args([])
        self.assertEqual(DEFAULT_PER_SUBJECT_SOL_SPEND_USD, 15.0)
        self.assertEqual(args.per_subject_sol_spend_limit_usd, 15.0)

    def test_every_subject_command_uses_explicit_revisit_mode_and_subject_ceiling(self) -> None:
        command = _subject_command(
            python="python",
            runner=Path("runner.py"),
            ticker="AAPL",
            root=Path("/home/ubuntu"),
            state_dir=Path("/home/ubuntu/campaign/01-aapl"),
            spend_limit_usd=15.0,
            dry_run=False,
        )
        self.assertIn("--revisit", command)
        self.assertEqual(command[command.index("--ticker") + 1], "AAPL")
        self.assertEqual(command[command.index("--sol-spend-limit-usd") + 1], "15.0")
        self.assertNotIn("--dry-run", command)

    def test_dry_run_is_forwarded_without_changing_revisit_semantics(self) -> None:
        command = _subject_command(
            python="python",
            runner=Path("runner.py"),
            ticker="XOM",
            root=Path("/home/ubuntu"),
            state_dir=Path("/home/ubuntu/campaign/11-xom"),
            spend_limit_usd=15.0,
            dry_run=True,
        )
        self.assertIn("--revisit", command)
        self.assertIn("--dry-run", command)


if __name__ == "__main__":
    unittest.main()
