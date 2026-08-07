from __future__ import annotations

import math
import statistics

from Engines.Analysis.methods.base import MethodResult, MethodValidationResult
from Engines.Analysis.models import CompatibilityAssessment, CompatibilityState


def _pearson(xs, ys):
    if len(xs) < 2:
        return None
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    if denom == 0:
        return None
    return sum(x*y for x, y in zip(dx, dy)) / denom


def _average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def _spearman(xs, ys):
    if len(xs) < 2:
        return None
    return _pearson(_average_ranks(xs), _average_ranks(ys))


class RelationshipRedundancyMethod:
    method_id = "analysis.relationship.redundancy"
    version = "1"

    def assess(self, context, inputs):
        return CompatibilityAssessment(state=CompatibilityState.COMPATIBLE, method_id=self.method_id)

    def execute(self, context, inputs, services):
        rows = tuple(inputs)
        columns = tuple(context.parameters.get("columns", ()))
        correlation_type = str(context.parameters.get("correlation_type", "pearson")).lower()
        if len(columns) < 2:
            raise ValueError("At least two columns are required")
        if correlation_type not in {"pearson", "spearman"}:
            raise ValueError("correlation_type must be pearson or spearman")

        pairs = []
        for i, left in enumerate(columns):
            for right in columns[i + 1:]:
                xs, ys = [], []
                for row in rows:
                    x, y = row.get(left), row.get(right)
                    if (
                        isinstance(x, (int, float)) and not isinstance(x, bool)
                        and isinstance(y, (int, float)) and not isinstance(y, bool)
                        and math.isfinite(float(x)) and math.isfinite(float(y))
                    ):
                        xs.append(float(x))
                        ys.append(float(y))
                value = _pearson(xs, ys) if correlation_type == "pearson" else _spearman(xs, ys)
                pairs.append({
                    "left": left,
                    "right": right,
                    "n": len(xs),
                    "correlation": value,
                })
        return MethodResult(
            scientific_result={
                "correlation_type": correlation_type,
                "pairs": pairs,
                "interpretation_boundary": "RELATIONSHIP_NOT_CAUSATION",
            }
        )

    def validate(self, result, context):
        pairs = result.scientific_result.get("pairs", [])
        finite_or_none = all(
            pair["correlation"] is None
            or (-1.0000000001 <= pair["correlation"] <= 1.0000000001)
            for pair in pairs
        )
        return MethodValidationResult(
            passed=bool(pairs) and finite_or_none,
            reasons=(() if pairs and finite_or_none else ("invalid relationship output",)),
        )
