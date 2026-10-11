"""Fail-closed V3 calibration evidence gate.

This gate deliberately does not invent scientific thresholds. A PASS requires
independent, already-computed, per-case statistical and recovery evidence.
Unknown or missing measurements are failures, never implicit passes.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Mapping

SHAPES = ("FAST", "MEDIUM", "SLOW")
EFFECTS = (0.0, 0.0025, 0.005, 0.01, 0.02)
REQUIRED_CASE_KEYS = (
    "family", "shape", "effect", "target_baseline_evaluated",
    "target_region_positive_lcb95", "target_region_overlap",
    "null_target_specific_recovery", "ga_preserves_or_improves",
    "full_63_day_curve", "independent_effective_n_verified",
    "causal_costs_verified", "long_short_evaluated_separately",
)


def certify_calibration(cases: list[Mapping], *, frozen_parameters_verified: bool) -> dict:
    failures = []
    groups = defaultdict(dict)
    if not frozen_parameters_verified:
        failures.append("frozen scientific parameters not independently verified")
    for index, case in enumerate(cases):
        missing = [k for k in REQUIRED_CASE_KEYS if k not in case]
        if missing:
            failures.append(f"case {index}: missing {missing}")
            continue
        try:
            key = (str(case["family"]), str(case["shape"]))
            effect = float(case["effect"])
        except (ValueError, TypeError):
            failures.append(f"case {index}: invalid identity/effect")
            continue
        if key[1] not in SHAPES or effect not in EFFECTS:
            failures.append(f"case {index}: unexpected shape/effect")
            continue
        if effect in groups[key]:
            failures.append(f"duplicate case: {key}, {effect}")
        groups[key][effect] = case
        for field in (
            "target_baseline_evaluated", "full_63_day_curve",
            "independent_effective_n_verified", "causal_costs_verified",
            "long_short_evaluated_separately",
        ):
            if case[field] is not True:
                failures.append(f"{key} {effect}: {field} not verified")
        if effect == 0:
            if case["null_target_specific_recovery"] is not False:
                failures.append(f"{key}: null target-specific recovery not rejected")
        elif effect == 0.02:
            for field in ("target_region_positive_lcb95", "target_region_overlap", "ga_preserves_or_improves"):
                if case[field] is not True:
                    failures.append(f"{key}: strong-effect {field} failed")
    if not groups:
        failures.append("no evaluated families")
    for family in {f for f, _ in groups}:
        for shape in SHAPES:
            present = set(groups.get((family, shape), {}))
            missing = set(EFFECTS) - present
            if missing:
                failures.append(f"{family}/{shape}: missing effect ladder {sorted(missing)}")
    return {
        "decision": "FAIL" if failures else "PASS",
        "failed_criteria": failures,
        "case_count": len(cases),
        "families": sorted({f for f, _ in groups}),
        "certification_scope": "structural and supplied statistical evidence only",
    }
