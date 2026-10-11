"""State-aware cash-first risk transition; no brokerage integration or invented duration."""
from dataclasses import dataclass
from .defensive_opportunity_gate import crash_transition_actions, evaluate_entry, Decision

@dataclass
class DefensiveStateController:
    defensive: bool = False
    cash_transition_confirmed: bool = False

    def update(self, *, abc_crash_detected: bool, r1_confirmed: bool):
        """A/B/C overrides simultaneous R-1; R-1 alone releases Defensive."""
        if abc_crash_detected:
            if not self.defensive:
                self.defensive = True
                self.cash_transition_confirmed = False
                return crash_transition_actions(True)
            return ()
        if self.defensive and r1_confirmed:
            self.defensive = False
            self.cash_transition_confirmed = False
        return ()

    def acknowledge_cash_transition(self, *, cancellations_confirmed: bool, liquidations_confirmed: bool):
        if self.defensive and cancellations_confirmed and liquidations_confirmed:
            self.cash_transition_confirmed = True

    def assess(self, **kwargs) -> Decision:
        if self.defensive and not self.cash_transition_confirmed:
            return Decision(False, 'cash_transition_unconfirmed')
        return evaluate_entry(defensive=self.defensive, **kwargs)
