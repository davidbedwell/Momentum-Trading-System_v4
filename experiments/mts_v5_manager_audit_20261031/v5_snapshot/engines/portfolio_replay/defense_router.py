"""Causal defensive state interface for research replay.

Decision made after session t close becomes effective at t+1 open.
External A_v2/B/B1/C and R-1 controllers must provide the state.
"""
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class DefenseDecision:
    decided_at: str
    effective_at: str
    defensive: bool
    triggers: tuple = ()
    recovery_authorized: bool = False

    def __post_init__(self):
        if date.fromisoformat(self.effective_at)<=date.fromisoformat(self.decided_at):
            raise ValueError("defense must not execute before next session")
        if self.defensive and self.recovery_authorized:
            raise ValueError("conflicting defensive/recovery state")
        if any(t not in ("A_v2","B","B1","C") for t in self.triggers):
            raise ValueError("unknown defense trigger")

class DefenseRouter:
    def __init__(self):
        self.defensive=False
        self.last_decision=None

    def apply(self,session,decision=None):
        """Use only decisions effective on or before session; no lookahead."""
        if decision is not None:
            if date.fromisoformat(decision.effective_at)>date.fromisoformat(session):
                raise ValueError("future defense decision")
            if self.last_decision and decision.decided_at<=self.last_decision.decided_at:
                raise ValueError("out of order defense decision")
            if decision.defensive:self.defensive=True
            elif self.defensive and decision.recovery_authorized:self.defensive=False
            self.last_decision=decision
        return self.defensive
