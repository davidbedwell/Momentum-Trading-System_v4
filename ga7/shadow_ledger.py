"""Independent chromosome shadow ledger. No capital is allocated here."""
from dataclasses import asdict
import json

class ShadowLedger:
    def __init__(self):
        self.requests = []
        self.outcomes = []

    def record(self, proposal):
        proposal.validate()
        self.requests.append(asdict(proposal))

    def settle(self, chromosome_id, ticker, session, realized_net_return,
               target_achieved, horizon_sessions):
        if not any(r["chromosome_id"] == chromosome_id and
                   r["ticker"] == ticker and r["session"] == session
                   for r in self.requests):
            raise ValueError("Outcome without original proposal")
        if not isinstance(target_achieved, bool) or not 1 <= horizon_sessions <= 40:
            raise ValueError("Invalid outcome")
        from math import isfinite
        if not isfinite(realized_net_return):
            raise ValueError("Invalid realized return")
        self.outcomes.append(dict(chromosome_id=chromosome_id, ticker=ticker,
            session=session, realized_net_return=realized_net_return,
            target_achieved=target_achieved, horizon_sessions=horizon_sessions))

    def jsonl(self):
        return "".join(json.dumps({"kind": "request", **r}, sort_keys=True) + "\n"
                       for r in self.requests) + "".join(
                       json.dumps({"kind": "outcome", **r}, sort_keys=True) + "\n"
                       for r in self.outcomes)
