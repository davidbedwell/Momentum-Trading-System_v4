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

    # Thresholds depend only on the feature column and requested quantile, not
    # on the current row. Cache them per candidate so we preserve identical
    # quantile semantics without re-sorting the full history once per row.
    quantile_cache: dict[tuple[str, float], float | None] = {}

    def qthreshold(feature: str, q: float) -> float | None:
        key = (feature, float(q))
        if key not in quantile_cache:
            vals = [_finite(r.get(feature)) for r in rows]
            clean = [v for v in vals if v is not None]
            quantile_cache[key] = None if not clean else _quantile(clean, q)
        return quantile_cache[key]

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
            rt = qthreshold(f, float(g["range_threshold_quantile"]))
            ok = rt is not None and _feature_predicate(row, f, "ABOVE", rt)
            pf = g["participation_feature"]
            if ok and pf != "NONE":
                pt = qthreshold(pf, float(g["participation_threshold_quantile"]))
                ok = pt is not None and _feature_predicate(row, pf, "ABOVE", pt)
            vf = g["volatility_feature"]
            if ok and vf != "NONE":
                vq = float(g["volatility_threshold_quantile"])
                vt = qthreshold(vf, vq if g["volatility_state"]=="HIGH" else 1.0-vq)
                ok = vt is not None and _feature_predicate(row, vf, g["volatility_state"], vt)
            signal[i] = ok
        elif family == "TREND":
            tf=g["trend_feature"]; tq=float(g["threshold_quantile"])
            tt=qthreshold(tf, tq if g["direction"]=="ABOVE" else 1.0-tq)
            ok = tt is not None and _feature_predicate(row, tf, g["direction"], tt)
            cf = g["confirmation_feature"]
            if ok and cf != "NONE":
                cq=float(g["confirmation_threshold_quantile"])
                ct=qthreshold(cf, cq if g["confirmation_direction"]=="ABOVE" else 1.0-cq)
                ok = ct is not None and _feature_predicate(row, cf, g["confirmation_direction"], ct)
            signal[i] = ok
        elif family == "MEAN_REVERSION":
            f = g["displacement_feature"]; tail = g["tail"]; sev = float(g["severity"])
            t = qthreshold(f, sev if tail == "LOW" else 1.0-sev)
            ok = t is not None and _feature_predicate(row, f, tail, t)
            cf = g["context_feature"]
            if ok and cf != "NONE":
                cq=float(g["context_threshold_quantile"])
                ct=qthreshold(cf, cq if g["context_state"]=="HIGH" else 1.0-cq)
                ok = ct is not None and _feature_predicate(row, cf, g["context_state"], ct)
            signal[i] = ok
        elif family == "VOLATILITY":
            f = g["volatility_feature"]; state = g["state"]; q = float(g["threshold_quantile"])
            t = qthreshold(f, q if state == "HIGH" else 1.0 - q)
            ok = t is not None and _feature_predicate(row, f, state, t)
            pf = g["price_context"]
            if ok and pf != "NONE":
                # v1 grammar has no separate price-context direction/threshold
                # genes. Give the declared context actual filtering semantics:
                # require the selected context to be at/above its median.
                pt = qthreshold(pf, 0.50)
                ok = pt is not None and _feature_predicate(row, pf, "ABOVE", pt)
            signal[i] = ok
        elif family == "VOLUME_LIQUIDITY":
            pf=g["participation_feature"]; q=float(g["threshold_quantile"])
            pt=qthreshold(pf, q if g["state"]=="HIGH" else 1.0-q)
            ok=pt is not None and _feature_predicate(row,pf,g["state"],pt)
            price=g["price_feature"]
            if ok and price!="NONE":
                pq=float(g["price_threshold_quantile"])
                pth=qthreshold(price,pq if g["price_direction"]=="ABOVE" else 1.0-pq)
                ok=pth is not None and _feature_predicate(row,price,g["price_direction"],pth)
            signal[i]=ok
        elif family == "RELATIVE_CROSS_SECTIONAL":
            rf=g["relative_feature"]; q=float(g["threshold_quantile"])
            rt=qthreshold(rf,q if g["tail"]=="LEADER" else 1.0-q)
            ok=rt is not None and _feature_predicate(row,rf,g["tail"],rt)
            mf=g["market_context"]
            if ok and mf!="NONE":
                ok=_feature_predicate(row,mf,g["market_context_state"],float(g["market_context_threshold"]))
            signal[i]=ok
        elif family == "EVENT_EARNINGS":
            f=g["reaction_feature"]
            signal[i] = _feature_predicate(row, f, g["reaction_direction"], float(g["reaction_threshold"]))
        elif family == "MARKET_REGIME_STRUCTURE":
            f=g["breadth_feature"]; state=g["breadth_state"]; t=float(g["breadth_threshold"])
            v=_finite(row.get(f))
            ok = False if v is None else (v < t if state=="LOW" else v > t if state=="HIGH" else abs(v-t) <= 0.10)
            sf=g["security_context"]
            if ok and sf!="NONE":
                sq=float(g["security_context_threshold_quantile"])
                st=qthreshold(sf,sq if g["security_context_direction"]=="ABOVE" else 1.0-sq)
                ok=st is not None and _feature_predicate(row,sf,g["security_context_direction"],st)
            signal[i]=ok
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
    fitness_valid = mean is not None
    search_fitness = -1.0e12 if mean is None else mean - (0.5 * se if se is not None else 0.0)
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
        "fitness_valid": fitness_valid,
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
