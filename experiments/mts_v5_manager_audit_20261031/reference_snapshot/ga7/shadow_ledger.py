"""Independent chromosome shadow ledger. No capital is allocated here."""
import json

class ShadowLedger:
    def __init__(self):
        self.requests = []
        self.outcomes = []
        self._request_keys = set()

    def record(self, proposal):
        proposal.validate()
        self.requests.append({
            "session":proposal.session, "ticker":proposal.ticker,
            "chromosome_id":proposal.chromosome_id, "action":proposal.action,
            "probability":proposal.probability,
            "expected_net_return":proposal.expected_net_return,
            "downside_risk":proposal.downside_risk,
            "requested_weight":proposal.requested_weight,
            "horizon_sessions":proposal.horizon_sessions,
            "confidence":proposal.confidence, "calibrated":proposal.calibrated})
        self._request_keys.add((proposal.chromosome_id, proposal.ticker, proposal.session))

    def settle(self, chromosome_id, ticker, session, realized_net_return,
               target_achieved, horizon_sessions):
        if (chromosome_id, ticker, session) not in self._request_keys:
            raise ValueError("Outcome without original proposal")
        if not isinstance(target_achieved, bool) or horizon_sessions < 1:
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
