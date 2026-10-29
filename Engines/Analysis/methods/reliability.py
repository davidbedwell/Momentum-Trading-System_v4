from __future__ import annotations

import math
import statistics

from Engines.Analysis.methods.base import MethodResult, MethodValidationResult
from Engines.Analysis.models import CompatibilityAssessment, CompatibilityState


# Transparent normal critical values for the first bounded implementation.
_Z = {
    0.90: 1.6448536269514722,
    0.95: 1.959963984540054,
    0.99: 2.5758293035489004,
}


class BasicStatisticalReliabilityMethod:
    method_id = "analysis.reliability.basic"
    version = "1"

    def assess(self, context, inputs):
        return CompatibilityAssessment(state=CompatibilityState.COMPATIBLE, method_id=self.method_id)

    def execute(self, context, inputs, services):
        rows = tuple(inputs)
        column = context.parameters.get("column")
        confidence = float(context.parameters.get("confidence_level", 0.95))
        if not column:
            raise ValueError("column parameter is required")
        if confidence not in _Z:
            raise ValueError("confidence_level must be one of 0.90, 0.95, 0.99")

        values = [
            float(row[column])
            for row in rows
            if isinstance(row.get(column), (int, float))
            and not isinstance(row.get(column), bool)
            and math.isfinite(float(row[column]))
        ]
        n = len(values)
        mean = statistics.fmean(values) if values else None
        sample_sd = statistics.stdev(values) if n >= 2 else None
        standard_error = sample_sd / math.sqrt(n) if sample_sd is not None else None
        margin = _Z[confidence] * standard_error if standard_error is not None else None
        ci = (
            {"lower": mean - margin, "upper": mean + margin}
            if mean is not None and margin is not None
            else None
        )
        return MethodResult(
            scientific_result={
                "column": column,
                "n": n,
                "mean": mean,
                "sample_stddev": sample_sd,
                "standard_error": standard_error,
                "confidence_level": confidence,
                "normal_approximation_mean_ci": ci,
                "limitations": [
                    "Normal-approximation interval; applicability depends on sample and distribution.",
                    "Statistical reliability is not economic significance or predictive validity.",
                ],
            },
            limitations=(
                "Normal-approximation interval; applicability depends on sample and distribution.",
                "Statistical reliability is not economic significance or predictive validity.",
            ),
        )

    def validate(self, result, context):
        n = result.scientific_result.get("n", 0)
        return MethodValidationResult(
            passed=n >= 2,
            reasons=(() if n >= 2 else ("at least two finite observations are required",)),
        )
