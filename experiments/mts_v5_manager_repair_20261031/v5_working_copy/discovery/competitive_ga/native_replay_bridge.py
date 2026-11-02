"""Convert verified native GA6/GA7 requests into next-open replay signals.

Native scores are family-specific and cannot be ranked against each other
without a separately fitted, frozen calibration model.
"""
from dataclasses import dataclass
from .native_signal_contract import normalize_proposals
from .evidence_bridge import build_snapshot,to_scale_evidence,DatedDrawdown
from engines.portfolio_replay.kernel import Signal

@dataclass(frozen=True)
class RiskInputs:
    stop_distance: float
    gap_risk: float
    other_equity_risk: float = 0.

def signals_for_close(proposals,as_of,*,trades_by_chromosome,drawdown_by_chromosome,
                      independently_confirmed,held_positions,risk_inputs,
                      calibrated_priority=None,drawdown_marks_by_chromosome=None,
                      trusted_drawdown_hashes=None):
    """Produce requests; execution kernel alone authorizes allocations.

    held_positions: mapping ticker -> (current_weight, profitable).
    No native-score cross-family comparisons are permitted.
    """
    native=normalize_proposals(proposals,as_of)
    if len({p.ticker for p in native})!=len(native):
        raise ValueError("multiple proposals for same ticker need selector resolution")
    if len({p.family for p in native})>1 and calibrated_priority is None:
        raise ValueError("mixed GA6/GA7 proposals require calibrated selector")
    if calibrated_priority is not None:
        from math import isfinite
        for p in native:
            value = calibrated_priority.get(p.chromosome_id)
            if not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError("missing or invalid calibrated priority")
    result=[]
    for p in native:
        current,profitable=held_positions.get(p.ticker,(0.,False))
        evidence=None
        risk=risk_inputs.get(p.ticker)
        if p.target_weight>current and p.target_weight>.10:
            if risk is None:raise ValueError("risk inputs required for scale request")
            trades=trades_by_chromosome.get(p.chromosome_id,())
            dd=drawdown_by_chromosome.get(p.chromosome_id)
            # Undated or untraceable drawdown cannot authorize scaling.
            if isinstance(dd,DatedDrawdown):
                from datetime import date
                from math import isfinite
                if (dd.chromosome_id!=p.chromosome_id or not dd.source_hash
                    or date.fromisoformat(dd.measured_through)>=date.fromisoformat(as_of)
                    or not isfinite(dd.value) or not 0<=dd.value<=1):
                    raise ValueError("invalid dated drawdown provenance")
            from .drawdown_provenance import verify
            marks=(drawdown_marks_by_chromosome or {}).get(p.chromosome_id)
            trusted=(trusted_drawdown_hashes or {}).get(p.chromosome_id)
            if (trades and isinstance(dd,DatedDrawdown) and marks is not None
                and trusted is not None and trusted==dd.source_hash
                and verify(dd,marks,as_of)):
                snapshot=build_snapshot(p.chromosome_id,as_of,trades,
                    historical_mdd=dd.value,
                    independently_confirmed=p.chromosome_id in independently_confirmed)
                evidence=to_scale_evidence(snapshot,signal_confirmed=p.action in ("ADD","HOLD","ENTER"),
                    position_profitable=profitable)
        priority=(calibrated_priority[p.chromosome_id] if calibrated_priority is not None
                  else p.native_score)
        result.append(Signal(p.ticker,p.family,p.chromosome_id,p.target_weight,
            score=priority,scaling_evidence=evidence,
            stop_distance=risk.stop_distance if risk else None,
            gap_risk=risk.gap_risk if risk else None,
            other_equity_risk=risk.other_equity_risk if risk else 0.))
    return result
