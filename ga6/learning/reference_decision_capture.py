"""Immutable decision-time evidence capture around frozen GA6 structural_signal.

Captures the actual pre-close feature map, position state and action produced
by the frozen signal, without replacing its logic. Per-process serialized use.
"""
from threading import RLock
from copy import deepcopy
from math import isfinite
from ga5_feature_adapter import LEGACY
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
_LOCK=RLock()

def evaluate_with_decision_trace(evaluator_module, frame, genome, **kwargs):
    prepared = frame if isinstance(frame, PreparedSessions) else PreparedSessions(frame)
    fields = (genome.entry_feature, genome.hold_feature, genome.exit_feature,
              genome.regime_feature, genome.sizing_feature, genome.replace_feature)
    tree_fields = set()
    def collect(node):
        if "family" in node:
            tree_fields.add(node["family"])
        else:
            for child in node["children"]:
                collect(child)
    if kwargs.get("entry_tree") is not None:
        collect(kwargs["entry_tree"])
    pairs = tuple((name, LEGACY.get(name, name)) for name in set(fields) | tree_fields)
    identities = []
    for ds, rows, opens, closes in prepared.sessions:
        for ticker, row in rows.items():
            features = {}
            valid = True
            for name, source in pairs:
                value = row.get(source)
                if value is None:
                    if name in fields: valid = False; break
                    continue
                value = float(value)
                if not isfinite(value):
                    if name in fields: valid = False; break
                    continue
                features[name] = value
            if valid:
                identities.append((ds, ticker, closes[ticker], features))
    with _LOCK:
        original=evaluator_module.structural_signal
        decisions=[]
        def traced(g, features, position, close, entry_tree=None):
            action,weight=original(g,features,position,close,entry_tree)
            if len(decisions) >= len(identities):
                raise RuntimeError("more signals than PIT identities")
            ds, ticker, expected_close, expected_features = identities[len(decisions)]
            if float(close) != float(expected_close) or features != expected_features:
                raise RuntimeError("signal inputs do not match chronological ticker identity")
            decisions.append({
                "decision_date":ds, "symbol":ticker,
                "evidence_cutoff":ds,
                "sequence":len(decisions),
                "action":action,"weight":weight,
                "features":deepcopy(features),
                "close":float(close),
                "position":{"shares":position.shares,
                            "entry_price":position.entry_price,
                            "peak_price":position.peak_price,
                            "sessions_held":position.sessions_held},
                "evidence_status":"PIT_SESSION_AND_TICKER_MATCHED",
            })
            return action,weight
        evaluator_module.structural_signal=traced
        try:
            metrics=evaluator_module.evaluate(frame,genome,**kwargs)
        finally:
            evaluator_module.structural_signal=original
        if len(decisions)!=len(identities) or len(decisions)!=metrics["signal_trace"]["feature_valid"]:
            raise RuntimeError("signal trace count differs from evaluator")
        return {"metrics":metrics,"decision_signals":decisions,
                "status":"CHRONOLOGICAL_SIGNAL_IDENTITIES_VERIFIED_NOT_EXECUTION_LINKED"}
