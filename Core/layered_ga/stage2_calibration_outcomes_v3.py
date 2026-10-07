"""Outcome-only planted-response calibration primitives for Stage 2 V3.

This module separates the *experiment constructor*, which knows the plant mask,
from the *candidate evaluator*, which receives only the resulting outcome paths.
No planted target or effect magnitude is passed to the GA fitness evaluator.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from Core.layered_ga.stage2_path_v3 import ExecutionPaths, ProspectiveCosts
from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation, evaluate_curve


@dataclass(frozen=True)
class PlantedExperiment:
    paths: ExecutionPaths
    target_rows: int
    effect: float
    profile: np.ndarray


def plant_endpoint_outcomes(
    paths: ExecutionPaths, target_mask: np.ndarray, profile: np.ndarray, effect: float
) -> PlantedExperiment:
    """Add a deterministic synthetic cumulative response to valid target outcomes.

    Copy-on-write: input paths are never modified. Excursion matrices remain
    unchanged, so MAE/MFE on planted outcomes are *not* calibrated by this
    operation and must not be interpreted as synthetic ground truth.
    """
    target = np.asarray(target_mask, dtype=bool)
    profile = np.asarray(profile, dtype=np.float64)
    endpoint = paths.endpoint_return
    if endpoint.ndim != 2 or target.shape != (endpoint.shape[0],):
        raise ValueError("plant mask and outcome rows are misaligned")
    if profile.shape != (endpoint.shape[1],) or not np.isfinite(profile).all():
        raise ValueError("plant profile and outcome horizons are misaligned")
    if not np.isfinite(effect) or effect < 0:
        raise ValueError("plant effect must be finite and nonnegative")
    new_endpoint = endpoint.copy()
    valid = target[:, None] & np.isfinite(endpoint)
    uplift = np.broadcast_to(effect * profile[None, :], endpoint.shape)
    new_endpoint[valid] = (endpoint[valid].astype(np.float64) + uplift[valid]).astype(endpoint.dtype)
    return PlantedExperiment(
        paths=ExecutionPaths(new_endpoint, paths.low_excursion, paths.high_excursion, paths.calendar_days),
        target_rows=int(target.sum()), effect=float(effect), profile=profile.copy()
    )


class OutcomeOnlyCurveEvaluator:
    """GA-facing evaluator: no target mask, effect size or shape oracle.

    The score is intentionally NOT defined here: selection must use the frozen
    scientific/economic multiobjective contract, not an invented scalar.
    """
    def __init__(self, compiler, paths: ExecutionPaths, costs: ProspectiveCosts, cluster_ids: np.ndarray):
        self.compiler = compiler
        self.paths = paths
        self.costs = costs
        self.cluster_ids = np.asarray(cluster_ids)

    def evaluate(self, family: str, genome: dict, side: str) -> CurveEvaluation:
        mask = self.compiler.compile(family, genome)
        return evaluate_curve(mask, self.paths, self.costs, side, self.cluster_ids)


def response_delta(
    planted: CurveEvaluation, null: CurveEvaluation
) -> tuple[dict, ...]:
    """Paired descriptive differences; *not* a statistical significance test."""
    if planted.side != null.side or len(planted.points) != len(null.points):
        raise ValueError("unmatched curve evaluations")
    result = []
    for a, b in zip(planted.points, null.points):
        if a["horizon"] != b["horizon"]:
            raise ValueError("unmatched horizons")
        av, bv = a.get("ev_net", np.nan), b.get("ev_net", np.nan)
        result.append({
            "horizon": a["horizon"],
            "delta_ev_net": float(av - bv) if np.isfinite(av) and np.isfinite(bv) else float("nan"),
            "planted_lcb95": a.get("lcb95", float("nan")),
            "null_lcb95": b.get("lcb95", float("nan")),
            "planted_effective_n": a.get("effective_n", 0),
            "null_effective_n": b.get("effective_n", 0),
        })
    return tuple(result)
