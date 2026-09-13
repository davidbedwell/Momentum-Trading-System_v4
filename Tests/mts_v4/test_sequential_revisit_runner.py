from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.run_sol_sequential_revisits import (
    DEFAULT_PER_SUBJECT_SOL_SPEND_USD,
    SEQUENCE,
    _parser,
    _subject_command,
)
from scripts.run_sol_batched_one_subject import _interactive_spend_authorization


class SequentialRevisitRunnerTests(unittest.TestCase):
    def test_governed_sequence_contains_all_eleven_prior_tickers(self) -> None:
        self.assertEqual(
            SEQUENCE,
            ("AAPL", "AMD", "AMZN", "BA", "GOOGL", "JPM", "META", "MSFT", "NVDA", "TSLA", "XOM"),
        )

    def test_default_spend_ceiling_is_five_dollars_per_subject(self) -> None:
        args = _parser().parse_args([])
        self.assertEqual(DEFAULT_PER_SUBJECT_SOL_SPEND_USD, 5.0)
        self.assertEqual(args.per_subject_sol_spend_limit_usd, 5.0)

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

    def test_background_authorization_prompt_stops_cleanly_when_stdin_is_closed(self) -> None:
        class Snapshot:
            authorized_spend_usd = 15.0
            actual_spend_usd = 14.78
            completed_sol_calls = 22
            estimated_percent_complete = 93.0
            estimated_remaining_batches = 2
            estimated_remaining_sol_calls = 2
            estimated_additional_spend_low_usd = 1.11
            estimated_additional_spend_high_usd = 1.34
            estimated_total_spend_low_usd = 15.90
            estimated_total_spend_high_usd = 16.13
            estimate_confidence = "medium-high"
            estimate_rationale = "remaining work"
            recommended_authorized_ceiling_usd = 20.0

        with patch("builtins.input", side_effect=OSError(9, "Bad file descriptor")):
            self.assertIsNone(_interactive_spend_authorization(Snapshot()))


if __name__ == "__main__":
    unittest.main()
