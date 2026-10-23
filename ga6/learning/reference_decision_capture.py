"""Immutable decision-time evidence capture around frozen GA6 structural_signal.

Captures the actual pre-close feature map, position state and action produced
by the frozen signal, without replacing its logic. Per-process serialized use.
"""
from threading import RLock
from copy import deepcopy
_LOCK=RLock()

def evaluate_with_decision_trace(evaluator_module, frame, genome, **kwargs):
    with _LOCK:
        original=evaluator_module.structural_signal
        decisions=[]
        def traced(g, features, position, close, entry_tree=None):
            action,weight=original(g,features,position,close,entry_tree)
            decisions.append({
                "sequence":len(decisions),
                "action":action,"weight":weight,
                "features":deepcopy(features),
                "close":float(close),
                "position":{"shares":position.shares,
                            "entry_price":position.entry_price,
                            "peak_price":position.peak_price,
                            "sessions_held":position.sessions_held},
                "evidence_status":"SIGNAL_INPUT_CAPTURED_NO_DATE_OR_SYMBOL",
            })
            return action,weight
        evaluator_module.structural_signal=traced
        try:
            metrics=evaluator_module.evaluate(frame,genome,**kwargs)
        finally:
            evaluator_module.structural_signal=original
        if len(decisions)!=metrics["signal_trace"]["feature_valid"]:
            raise RuntimeError("signal trace count differs from evaluator")
        return {"metrics":metrics,"decision_signals":decisions,
                "status":"SIGNAL_INPUTS_CAPTURED_NOT_YET_DECISION_ID_CERTIFIED"}
