import unittest
from ga7.proposals import Proposal, rank_proposals
from ga7.shadow_ledger import ShadowLedger

class ProposalContractTests(unittest.TestCase):
    def proposal(self, **changes):
        fields = dict(session=4, ticker="TEST", chromosome_id="genome-a",
            action="ENTER", probability=.65, expected_net_return=.08,
            downside_risk=.04, requested_weight=.08, horizon_sessions=15,
            confidence=.7, calibrated=False)
        fields.update(changes)
        return Proposal(**fields)

    def test_valid_entry_and_shadow_outcome(self):
        p = self.proposal().validate()
        ledger = ShadowLedger()
        ledger.record(p)
        ledger.settle(p.chromosome_id, p.ticker, p.session, .06, True, 15)
        self.assertEqual(len(ledger.requests), 1)
        self.assertEqual(len(ledger.outcomes), 1)
        self.assertIn('"kind": "request"', ledger.jsonl())

    def test_probability_is_not_implicitly_calibrated(self):
        self.assertFalse(self.proposal().calibrated)

    def test_invalid_request_rejected(self):
        for changes in (dict(probability=1.2), dict(requested_weight=.31),
                        dict(horizon_sessions=41),
                        dict(action="EXIT", requested_weight=.1)):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.proposal(**changes).validate()

    def test_rank_does_not_allocate(self):
        ranked = rank_proposals([self.proposal(chromosome_id="a"),
            self.proposal(chromosome_id="b", expected_net_return=.02)])
        self.assertEqual(ranked[0].chromosome_id, "a")

if __name__ == "__main__":
    unittest.main()
