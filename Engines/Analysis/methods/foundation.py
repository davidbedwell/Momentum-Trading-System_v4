from __future__ import annotations

from typing import Any, Mapping, Sequence

from Engines.Analysis.methods.base import MethodResult, MethodValidationResult
from Engines.Analysis.models import CompatibilityAssessment, CompatibilityState


class FoundationDatasetIntrospectionMethod:
    method_id = "analysis.foundation.dataset-introspection"
    version = "1"

    def assess(self, context, inputs):
        return CompatibilityAssessment(
            state=CompatibilityState.COMPATIBLE,
            method_id=self.method_id,
        )

    def execute(self, context, inputs, services):
        rows = tuple(inputs)
        columns = sorted({str(key) for row in rows for key in row.keys()})
        missingness = {
            column: sum(1 for row in rows if row.get(column) is None)
            for column in columns
        }
        dates = sorted(
            str(row["date"])
            for row in rows
            if row.get("date") is not None
        )
        measurement_columns = tuple(
            column
            for column in columns
            if column not in {"ticker", "symbol", "date", "open", "high", "low", "close", "volume"}
        )
        retrospective_markers = ("forward_", "future_", "mfe", "mae", "time_to_", "threshold_")
        outcome_columns = tuple(
            column for column in columns
            if any(marker in column.lower() for marker in retrospective_markers)
        )
        result = {
            "row_count": len(rows),
            "available_columns": columns,
            "temporal_coverage": {
                "start": dates[0] if dates else None,
                "end": dates[-1] if dates else None,
            },
            "missingness": missingness,
            "measurement_columns": list(measurement_columns),
            "outcome_columns": list(outcome_columns),
        }
        return MethodResult(
            scientific_result=result,
            sample_record={"row_count": len(rows)},
        )

    def validate(self, result, context):
        required = {"row_count", "available_columns", "missingness", "measurement_columns", "outcome_columns"}
        missing = tuple(sorted(required - set(result.scientific_result)))
        return MethodValidationResult(
            passed=not missing,
            reasons=(() if not missing else (f"missing result fields: {missing}",)),
        )
