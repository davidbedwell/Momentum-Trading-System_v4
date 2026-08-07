from __future__ import annotations

import math
import statistics
from typing import Any, Sequence

from Engines.Analysis.methods.base import MethodResult, MethodValidationResult
from Engines.Analysis.models import CompatibilityAssessment, CompatibilityState


def _finite_numeric(values):
    return [
        float(v) for v in values
        if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))
    ]


def _quantile(sorted_values, q: float):
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    weight = pos - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


class DescriptiveStatisticsMethod:
    method_id = "analysis.descriptive.statistics"
    version = "1"

    def assess(self, context, inputs):
        return CompatibilityAssessment(state=CompatibilityState.COMPATIBLE, method_id=self.method_id)

    def execute(self, context, inputs, services):
        rows = tuple(inputs)
        requested = tuple(context.parameters.get("columns", ()))
        if not requested:
            requested = tuple(sorted({
                key for row in rows for key, value in row.items()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            }))
        summaries = {}
        for column in requested:
            raw = [row.get(column) for row in rows]
            values = sorted(_finite_numeric(raw))
            summaries[column] = {
                "count": len(values),
                "missing_count": sum(v is None for v in raw),
                "mean": statistics.fmean(values) if values else None,
                "median": statistics.median(values) if values else None,
                "stddev_sample": statistics.stdev(values) if len(values) >= 2 else None,
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
                "q05": _quantile(values, 0.05),
                "q25": _quantile(values, 0.25),
                "q75": _quantile(values, 0.75),
                "q95": _quantile(values, 0.95),
            }
        return MethodResult(
            scientific_result={
                "row_count": len(rows),
                "columns": summaries,
                "interpretation_boundary": "DESCRIPTIVE_ONLY",
            }
        )

    def validate(self, result, context):
        ok = result.scientific_result.get("interpretation_boundary") == "DESCRIPTIVE_ONLY"
        return MethodValidationResult(
            passed=ok,
            reasons=(() if ok else ("descriptive boundary missing",)),
        )
