"""GA4 candidate-level conditional relationship evidence, independent of portfolio CAGR/MDD."""
from __future__ import annotations

import hashlib
import json

from .ga4_horizon_contract import validate_horizons


def candidate_key(chromosomes, context):
    """Stable ID for an ordered chromosome combination in an explicit environment."""
    chromosomes = tuple(chromosomes)
    if not 1 <= len(chromosomes) <= 4:
        raise ValueError("GA4 requires one to four chromosomes")
    if len(set(chromosomes)) != len(chromosomes):
        raise ValueError("Duplicate chromosomes in candidate")
    if not isinstance(context, dict) or not context:
        raise ValueError("Context must be an explicit nonempty mapping")
    payload = json.dumps({"chromosomes": chromosomes, "context": context}, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def relationship_record(*, chromosomes, context, curve, fold, data_provenance):
    """Preserve the full 63-point curve, including negative and unavailable evidence.

    No CAGR/MDD-based pruning occurs here. Fold and provenance must be explicit.
    """
    if not fold or not data_provenance:
        raise ValueError("Fold and data provenance are required")
    points = [dict(p) for p in curve.points]
    validate_horizons(p["horizon"] for p in points)
    required = ("ev_net", "mae_mean", "n", "effective_n")
    for point in points:
        if any(field not in point for field in required):
            raise ValueError("Missing EV/MAE or sample-size evidence")
    return {
        "candidate_id": candidate_key(chromosomes, {**context, "trade_side": curve.side}),
        "chromosomes": list(chromosomes),
        "context": dict(context),
        "fold": fold,
        "data_provenance": data_provenance,
        "side": curve.side,
        "daily_horizon_evidence": points,
        "pareto_horizons": list(curve.pareto_horizons),
        "pareto_ranges": [list(r) for r in curve.pareto_ranges],
        "certified": False,
    }
