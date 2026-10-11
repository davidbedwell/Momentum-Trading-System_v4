"""GA-facing outcome-only evaluator for the V3 calibration runner.

This adapter intentionally cannot see the planted target mask or effect size.
It evaluates every integer horizon, but is NOT a substitute for the frozen
multiobjective scientific selection or the independent statistical gate.
"""
import numpy as np

from Core.layered_ga.stage2_calibration_outcomes_v3 import OutcomeOnlyCurveEvaluator
from Core.layered_ga.stage2_calibration_pareto_v3 import describe_front


class MatchedEvaluator:
    analysis_contract_version = "V3_OUTCOME_ONLY_FULL_PATH_V2"

    def __init__(self, compiler, paths, costs, cluster_ids, side="LONG"):
        self.curves = OutcomeOnlyCurveEvaluator(compiler, paths, costs, cluster_ids)
        self.side = side
        self.calls = 0
        self.best = float("-inf")
        self.ledger = []

    def evaluate(self, candidate, *, evidence_identity):
        from MTS_V4.computational_search import Evaluation

        curve = self.curves.evaluate(candidate.family_id, candidate.genome, self.side)
        valid = [p for p in curve.points if np.isfinite(p.get("lcb95", np.nan))]
        # Temporary conservative search proxy; no certification is allowed.
        score = max((float(p["lcb95"]) for p in valid), default=-1e6)
        self.calls += 1
        self.best = max(self.best, score)
        self.ledger.append({"candidate_id": candidate.candidate_id,
                            "score": score, "horizons": len(curve.points),
                            "pareto_front": describe_front(curve)})
        return Evaluation(candidate.candidate_id, evidence_identity,
                          self.analysis_contract_version, {"net_expectancy": score})
