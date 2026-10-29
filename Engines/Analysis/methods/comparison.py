from __future__ import annotations

import math
import statistics

from Engines.Analysis.methods.base import MethodResult, MethodValidationResult
from Engines.Analysis.models import CompatibilityAssessment, CompatibilityState


def _numeric(values):
    return [
        float(v) for v in values
        if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))
    ]


class CohortOutcomeComparisonMethod:
    method_id = "analysis.comparison.cohort-outcome"
    version = "1"

    def assess(self, context, inputs):
        return CompatibilityAssessment(state=CompatibilityState.COMPATIBLE, method_id=self.method_id)

    def execute(self, context, inputs, services):
        rows = tuple(inputs)
        outcome_column = context.parameters.get("outcome_column")
        group_column = context.parameters.get("group_column")
        if not outcome_column or not group_column:
            raise ValueError("outcome_column and group_column are required context parameters")

        groups = {}
        for row in rows:
            group = row.get(group_column)
            value = row.get(outcome_column)
            if group is None:
                continue
            groups.setdefault(str(group), []).append(value)

        summaries = {}
        for group, raw in sorted(groups.items()):
            values = _numeric(raw)
            summaries[group] = {
                "count": len(values),
                "mean": statistics.fmean(values) if values else None,
                "median": statistics.median(values) if values else None,
                "stddev_sample": statistics.stdev(values) if len(values) >= 2 else None,
            }

        group_names = sorted(summaries)
        pairwise = []
        for i, left in enumerate(group_names):
            for right in group_names[i + 1:]:
                lm = summaries[left]["mean"]
                rm = summaries[right]["mean"]
                pairwise.append({
                    "left_group": left,
                    "right_group": right,
                    "mean_difference": None if lm is None or rm is None else lm - rm,
                })

        return MethodResult(
            scientific_result={
                "outcome_column": outcome_column,
                "group_column": group_column,
                "groups": summaries,
                "pairwise_mean_differences": pairwise,
                "interpretation_boundary": "COHORT_COMPARISON_ONLY",
            }
        )

    def validate(self, result, context):
        groups = result.scientific_result.get("groups", {})
        ok = len(groups) >= 2
        return MethodValidationResult(
            passed=ok,
            reasons=(() if ok else ("at least two governed groups are required",)),
        )
