"""GA7 chromosome proposal contract: predictions are not portfolio orders.

A research evaluator may simulate these requests independently; only the
future MTS allocator can authorize real portfolio allocations.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Literal

Action = Literal["ENTER", "INCREASE", "HOLD", "REDUCE", "EXIT", "PASS"]

@dataclass(frozen=True)
class Proposal:
    session: int
    ticker: str
    chromosome_id: str
    action: Action
    probability: float
    expected_net_return: float
    downside_risk: float
    requested_weight: float
    horizon_sessions: int
    confidence: float
    calibrated: bool = False

    def validate(self):
        if self.session < 0 or not self.ticker or not self.chromosome_id:
            raise ValueError("Missing proposal identity")
        if self.action not in ("ENTER", "INCREASE", "HOLD", "REDUCE", "EXIT", "PASS"):
            raise ValueError("Unknown action")
        for value in (self.probability, self.expected_net_return,
                      self.downside_risk, self.requested_weight, self.confidence):
            if not isfinite(value):
                raise ValueError("Non-finite prediction")
        if not (0 <= self.probability <= 1 and 0 <= self.confidence <= 1):
            raise ValueError("Invalid probability or confidence")
        if not (0 <= self.downside_risk and 0 <= self.requested_weight <= .30):
            raise ValueError("Invalid risk or funding request")
        if not 1 <= self.horizon_sessions <= 40:
            raise ValueError("Invalid horizon")
        if self.action in ("ENTER", "INCREASE") and self.requested_weight <= 0:
            raise ValueError("Funding request must be positive")
        if self.action in ("EXIT", "PASS") and self.requested_weight != 0:
            raise ValueError("Exit/pass cannot request capital")
        return self

def rank_proposals(proposals):
    """Research-only deterministic priority; NOT an approved capital allocator."""
    checked = [p.validate() for p in proposals]
    return sorted(checked, key=lambda p: (
        -(p.probability * p.expected_net_return - (1-p.probability) * p.downside_risk),
        -p.confidence, p.chromosome_id, p.ticker
    ))
