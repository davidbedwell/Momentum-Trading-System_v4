from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .analysis import ExactMethodAnalysisExecutor, RegisteredAnalysisMethod
from .computational_search import Candidate, Evaluation, SearchGovernanceError
from .contracts import AnalysisRequest, ResearchPhase


METHOD_ID = "analysis.search_candidate.forward_return"
ANALYSIS_CONTRACT_VERSION = "search-candidate-forward-return.v1"


def _finite(value: object) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires data")
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    w = pos - lo
    return ordered[lo] * (1 - w) + ordered[hi] * w


def _feature_predicate(row: Mapping[str, Any], feature: str, mode: str, threshold: float) -> bool:
    value = _finite(row.get(feature))
    if value is None:
        return False
    if mode in {"ABOVE", "HIGH", "LEADER", "POSITIVE"}:
        return value >= threshold
    if mode in {"BELOW", "LOW", "LAGGARD", "NEGATIVE"}:
        return value <= threshold
    return False


def _compile_signal(rows: Sequence[Mapping[str, Any]], candidate: Mapping[str, Any]) -> list[bool]:
    family = str(candidate["family_id"])
    g = candidate["genome"]
    signal = [False] * len(rows)

    def qthreshold(feature: str, q: float) -> float | None:
        vals = [_finite(r.get(feature)) for r in rows]
        clean = [v for v in vals if v is not None]
        return None if not clean else _quantile(clean, q)

    for i, row in enumerate(rows):
        if family == "MOMENTUM":
            f = g["momentum_feature"]
            q = float(g["threshold_quantile"])
            t = qthreshold(f, q if g["direction"] == "ABOVE" else 1.0 - q)
            ok = t is not None and _feature_predicate(row, f, g["direction"], t)
            cf = g["context_feature"]
            if ok and cf != "NONE":
                cv = _finite(row.get(cf)); ok = cv is not None and cv >= float(g["context_threshold"])
            signal[i] = ok
        elif family == "BREAKOUT":
            f = g["range_feature"]
            ok = _feature_predicate(row, f, "ABOVE", float(g["range_threshold"]))
            pf = g["participation_feature"]
            if ok and pf != "NONE":
                ok = _feature_predicate(row, pf, "ABOVE", float(g["participation_threshold"]))
            vf = g["volatility_feature"]
            if ok and vf != "NONE":
                ok = _finite(row.get(vf)) is not None
            signal[i] = ok
        elif family == "TREND":
            ok = _feature_predicate(row, g["trend_feature"], g["direction"], float(g["threshold"]))
            cf = g["confirmation_feature"]
            if ok and cf != "NONE":
                ok = _finite(row.get(cf)) is not None
            signal[i] = ok
        elif family == "MEAN_REVERSION":
            f = g["displacement_feature"]; tail = g["tail"]; sev = float(g["severity"])
            t = qthreshold(f, sev if tail == "LOW" else 1.0-sev)
            ok = t is not None and _feature_predicate(row, f, tail, t)
            cf = g["context_feature"]
            if ok and cf != "NONE":
                ok = _finite(row.get(cf)) is not None
            signal[i] = ok
        elif family == "VOLATILITY":
            f = g["volatility_feature"]; state = g["state"]; q = float(g["threshold_quantile"])
            t = qthreshold(f, q)
            ok = t is not None and _feature_predicate(row, f, state, t)
            pf = g["price_context"]
            if ok and pf != "NONE":
                ok = _finite(row.get(pf)) is not None
            signal[i] = ok
        elif family == "VOLUME_LIQUIDITY":
            signal[i] = _feature_predicate(row, g["participation_feature"], g["state"], float(g["threshold"]))
        elif family == "RELATIVE_CROSS_SECTIONAL":
            signal[i] = _feature_predicate(row, g["relative_feature"], g["tail"], float(g["threshold"]))
        elif family == "EVENT_EARNINGS":
            f=g["reaction_feature"]
            signal[i] = _feature_predicate(row, f, g["reaction_direction"], float(g["reaction_threshold"]))
        elif family == "MARKET_REGIME_STRUCTURE":
            f=g["breadth_feature"]; state=g["breadth_state"]; t=float(g["breadth_threshold"])
            v=_finite(row.get(f))
            signal[i] = False if v is None else (v < t if state=="LOW" else v > t if state=="HIGH" else abs(v-t) <= 0.10)
        else:
            raise SearchGovernanceError(f"family not executable in one-subject v1 runner: {family}")
    return signal


def search_candidate_forward_return(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    predictors = evidence_payloads.get("predictors")
    outcomes = evidence_payloads.get("outcomes")
    if not isinstance(predictors, (list, tuple)) or not isinstance(outcomes, (list, tuple)):
        raise ValueError("predictors and outcomes are required")
    candidate = parameters["candidate"]
    horizon = int(candidate["genome"]["forward_horizon"])
    outcome_column = f"forward_return_{horizon}__v1"
    out_index = {(str(r["security_id"]), str(r["effective_date"])): r for r in outcomes if isinstance(r, Mapping)}
    rows = [r for r in predictors if isinstance(r, Mapping)]
    signals = _compile_signal(rows, candidate)
    realized = []
    for row, active in zip(rows, signals):
        if not active:
            continue
        out = out_index.get((str(row["security_id"]), str(row["effective_date"])))
        if out is None:
            continue
        value = _finite(out.get(outcome_column))
        if value is not None:
            realized.append(value)
    n = len(realized)
    mean = statistics.fmean(realized) if realized else None
    sd = statistics.stdev(realized) if n > 1 else None
    se = None if sd is None else sd / math.sqrt(n)
    hit = None if not realized else sum(v > 0 for v in realized) / n
    search_fitness = None if mean is None else mean - (0.5 * se if se is not None else 0.0)
    return {
        "candidate_id": candidate["candidate_id"],
        "family_id": candidate["family_id"],
        "forward_horizon": horizon,
        "signal_count": n,
        "mean_forward_return": mean,
        "standard_deviation": sd,
        "standard_error": se,
        "positive_fraction": hit,
        "search_fitness": search_fitness,
        "interpretation_boundary": "SEARCH_GUIDANCE_ONLY_NOT_SCIENTIFIC_VALIDATION_OR_TRADING_PROMOTION",
    }


def analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(METHOD_ID, search_candidate_forward_return)


@dataclass
class SearchCandidateAnalysisEvaluator:
    subject_id: str
    predictor_rows: Sequence[Mapping[str, Any]]
    outcome_rows: Sequence[Mapping[str, Any]]
    executor: ExactMethodAnalysisExecutor
    evidence_identity: str
    analysis_contract_version: str = ANALYSIS_CONTRACT_VERSION

    @classmethod
    def build(cls, *, subject_id: str, predictor_rows, outcome_rows, evidence_identity: str):
        executor = ExactMethodAnalysisExecutor()
        executor.register(analysis_method())
        return cls(subject_id, predictor_rows, outcome_rows, executor, evidence_identity)

    def evaluate(self, candidate: Candidate, *, evidence_identity: str) -> Evaluation:
        if evidence_identity != self.evidence_identity:
            raise SearchGovernanceError("candidate evaluator evidence identity mismatch")
        request = AnalysisRequest(
            request_id=f"search-eval:{candidate.candidate_id}",
            subject_id=self.subject_id,
            question="Mechanically evaluate candidate signal forward-return distribution on Discovery evidence.",
            method_id=METHOD_ID,
            evidence_ids=("predictors","outcomes"),
            parameters={"candidate": {
                "candidate_id": candidate.candidate_id,
                "family_id": candidate.family_id,
                "genome": dict(candidate.genome),
            }},
            research_phase=ResearchPhase.EXPLORATION,
            rationale="Governed Search/Analysis evaluation; scientific interpretation remains with RD.",
        )
        result = self.executor.execute(request, {"predictors": self.predictor_rows, "outcomes": self.outcome_rows})
        if result.execution_metadata.get("execution_status") != "SUCCESS":
            raise SearchGovernanceError(str(result.outputs.get("execution_error")))
        return Evaluation(
            candidate_id=candidate.candidate_id,
            evidence_identity=evidence_identity,
            analysis_contract_version=self.analysis_contract_version,
            metrics=dict(result.outputs),
            analysis_refs=(result.result_id,),
        )
