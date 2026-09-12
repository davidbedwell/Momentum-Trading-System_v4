from __future__ import annotations

import unittest

from MTS_V4.sol_spend_guard import (
    SolResearchProgressEstimate,
    SolSpendAuthorizationRequired,
    SolSpendGuard,
)


class SolSpendGuardTests(unittest.TestCase):
    def test_usage_cost_uses_sol_token_rates(self):
        usage = {
            "prompt_tokens": 1_000_000,
            "completion_tokens": 1_000_000,
            "prompt_tokens_details": {"cached_tokens": 0},
        }
        self.assertAlmostEqual(SolSpendGuard.estimate_usage_cost_usd(usage), 36.0, places=6)

    def test_cached_input_is_discounted(self):
        usage = {
            "prompt_tokens": 100_000,
            "completion_tokens": 10_000,
            "prompt_tokens_details": {"cached_tokens": 50_000},
        }
        expected = (50_000 / 1_000_000) * 4.0 + (50_000 / 1_000_000) * 0.4 + (10_000 / 1_000_000) * 20.0
        self.assertAlmostEqual(SolSpendGuard.estimate_usage_cost_usd(usage), expected, places=6)

    def test_progress_projection_combines_percent_complete_and_remaining_calls(self):
        guard = SolSpendGuard(authorized_spend_usd=20.0)
        guard.record_provider_usage(
            {
                "prompt_tokens": 500_000,
                "completion_tokens": 100_000,
                "prompt_tokens_details": {"cached_tokens": 0},
            }
        )
        guard.update_research_progress(
            SolResearchProgressEstimate(
                estimated_percent_complete=50.0,
                estimated_remaining_batches=2,
                estimated_remaining_sol_calls=2,
                estimate_confidence="medium",
                estimate_rationale="Two coherent follow-up batches remain.",
            )
        )
        snapshot = guard.snapshot()
        self.assertIsNotNone(snapshot.estimated_additional_spend_low_usd)
        self.assertIsNotNone(snapshot.estimated_additional_spend_high_usd)
        self.assertGreaterEqual(
            snapshot.estimated_additional_spend_high_usd,
            snapshot.estimated_additional_spend_low_usd,
        )
        self.assertEqual(snapshot.estimated_percent_complete, 50.0)
        self.assertEqual(snapshot.estimated_remaining_sol_calls, 2)

    def test_guard_requires_human_authorization_when_projected_need_exceeds_ceiling(self):
        guard = SolSpendGuard(authorized_spend_usd=20.0)
        guard.record_provider_usage(
            {
                "prompt_tokens": 1_000_000,
                "completion_tokens": 0,
                "prompt_tokens_details": {"cached_tokens": 0},
            }
        )
        guard.update_research_progress(
            SolResearchProgressEstimate(
                estimated_percent_complete=10.0,
                estimated_remaining_batches=5,
                estimated_remaining_sol_calls=5,
                estimate_confidence="low",
                estimate_rationale="Most scientific work remains.",
            )
        )
        with self.assertRaises(SolSpendAuthorizationRequired) as raised:
            guard.ensure_authorized_before_next_call()
        self.assertEqual(raised.exception.snapshot.authorized_spend_usd, 20.0)
        self.assertGreater(
            raised.exception.snapshot.estimated_total_spend_high_usd,
            20.0,
        )

    def test_human_can_authorize_higher_ceiling_without_changing_scientific_work(self):
        seen = []

        def authorize(snapshot):
            seen.append(snapshot)
            return 50.0

        guard = SolSpendGuard(
            authorized_spend_usd=20.0,
            authorization_callback=authorize,
        )
        guard.record_provider_usage(
            {
                "prompt_tokens": 1_000_000,
                "completion_tokens": 0,
                "prompt_tokens_details": {"cached_tokens": 0},
            }
        )
        guard.update_research_progress(
            SolResearchProgressEstimate(
                estimated_percent_complete=10.0,
                estimated_remaining_batches=5,
                estimated_remaining_sol_calls=5,
                estimate_confidence="low",
                estimate_rationale="Most scientific work remains.",
            )
        )
        snapshot = guard.ensure_authorized_before_next_call()
        self.assertEqual(len(seen), 1)
        self.assertEqual(snapshot.authorized_spend_usd, 50.0)
        self.assertEqual(snapshot.estimated_remaining_batches, 5)
        self.assertEqual(snapshot.estimated_remaining_sol_calls, 5)


if __name__ == "__main__":
    unittest.main()
