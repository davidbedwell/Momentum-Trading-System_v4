"""Causal counterfactual evidence ledger for research, not execution certification.

Outcomes are immutable and become visible only at their actual maturity date.
Portfolio counterfactuals require independent shared-kernel replay; this ledger
does not manufacture economic outcomes.
"""
from dataclasses import dataclass, asdict
from datetime import date
import json

@dataclass(frozen=True)
class Decision:
    decision_id: str
    decided_at: str
    ticker: str
    action: str
    selected: bool
    chromosome: str
    family: str
    feature_snapshot_hash: str
    regime_model_version: str
    niche_model_version: str
    defense_state: str
    reason: str

@dataclass(frozen=True)
class Outcome:
    decision_id: str
    observed_through: str
    matured_at: str
    scenario: str
    incremental_net_value: float
    replay_manifest_hash: str

class CausalLedger:
    def __init__(self):
        self.decisions={}
        self.outcomes={}
        self.learning_events=[]

    @staticmethod
    def _date(value):
        return date.fromisoformat(value)

    def record_decision(self, decision):
        if not decision.feature_snapshot_hash or not decision.decision_id:
            raise ValueError("decision must be reproducible")
        self._date(decision.decided_at)
        if decision.decision_id in self.decisions:
            raise ValueError("duplicate decision")
        self.decisions[decision.decision_id]=decision

    def record_outcome(self, outcome):
        decision=self.decisions.get(outcome.decision_id)
        if decision is None:
            raise ValueError("unknown decision")
        if not outcome.replay_manifest_hash:
            raise ValueError("unverifiable counterfactual replay")
        if self._date(outcome.observed_through)<self._date(decision.decided_at):
            raise ValueError("outcome predates decision")
        if self._date(outcome.matured_at)<self._date(outcome.observed_through):
            raise ValueError("outcome maturity precedes observation")
        key=(outcome.decision_id,outcome.scenario)
        if key in self.outcomes:
            raise ValueError("duplicate outcome")
        self.outcomes[key]=outcome

    def available(self, as_of):
        now=self._date(as_of)
        return tuple(o for _,o in sorted(self.outcomes.items())
                     if self._date(o.matured_at)<=now)

    def learn(self, as_of, policy_hash):
        if not policy_hash:
            raise ValueError("policy version required")
        eligible=self.available(as_of)
        event={"as_of":as_of,"policy_hash":policy_hash,
               "outcome_keys":tuple((o.decision_id,o.scenario) for o in eligible)}
        self.learning_events.append(event)
        return eligible

    def export_jsonl(self):
        lines=[]
        for d in self.decisions.values():
            lines.append(json.dumps({"kind":"decision",**asdict(d)},sort_keys=True))
        for o in self.outcomes.values():
            lines.append(json.dumps({"kind":"outcome",**asdict(o)},sort_keys=True))
        for event in self.learning_events:
            lines.append(json.dumps({"kind":"learning",**event},sort_keys=True))
        return "\n".join(lines)+"\n" if lines else ""
