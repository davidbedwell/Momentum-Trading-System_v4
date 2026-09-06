from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .contracts import AnalysisRequest, AnalysisResult


class AnalysisExecutionError(RuntimeError):
    pass


AnalysisCallable = Callable[[Mapping[str, object], Mapping[str, Any]], Mapping[str, Any]]


@dataclass(frozen=True, slots=True)
class RegisteredAnalysisMethod:
    method_id: str
    implementation: AnalysisCallable


class ExactMethodAnalysisExecutor:
    """Execute exactly the method named by the validated RD request.

    There is intentionally no fallback, family inference, ranking, or method
    substitution path in this executor. A method-level execution failure is
    returned as an objective Analysis result for RD to interpret or repair; it
    is never converted into a substitute scientific method or input.
    """

    def __init__(self) -> None:
        self._methods: dict[str, RegisteredAnalysisMethod] = {}
        self._sequence = 0

    def register(self, method: RegisteredAnalysisMethod) -> None:
        if not method.method_id.strip():
            raise ValueError("method_id cannot be blank")
        if method.method_id in self._methods:
            raise ValueError(f"duplicate analysis method: {method.method_id}")
        self._methods[method.method_id] = method

    def execute(
        self,
        request: AnalysisRequest,
        evidence_payloads: Mapping[str, object],
    ) -> AnalysisResult:
        try:
            registered = self._methods[request.method_id]
        except KeyError as exc:
            raise AnalysisExecutionError(
                f"validated method has no registered executor: {request.method_id}"
            ) from exc

        self._sequence += 1
        result_id = f"analysis-result:{self._sequence}"
        try:
            outputs = registered.implementation(evidence_payloads, request.parameters)
        except Exception as exc:
            return AnalysisResult(
                result_id=result_id,
                request_id=request.request_id,
                subject_id=request.subject_id,
                method_id=request.method_id,
                outputs={
                    "execution_error": f"{type(exc).__name__}: {exc}",
                    "interpretation_boundary": "OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP",
                },
                evidence_ids=request.evidence_ids,
                limitations=("Requested Analysis method did not complete successfully.",),
                execution_metadata={
                    "executor": "MTS_V4.ExactMethodAnalysisExecutor",
                    "execution_status": "ERROR",
                },
            )

        if not isinstance(outputs, Mapping):
            return AnalysisResult(
                result_id=result_id,
                request_id=request.request_id,
                subject_id=request.subject_id,
                method_id=request.method_id,
                outputs={
                    "execution_error": (
                        f"Analysis method returned {type(outputs).__name__}; required mapping"
                    ),
                    "interpretation_boundary": "OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP",
                },
                evidence_ids=request.evidence_ids,
                limitations=("Requested Analysis method returned an invalid execution shape.",),
                execution_metadata={
                    "executor": "MTS_V4.ExactMethodAnalysisExecutor",
                    "execution_status": "ERROR",
                },
            )

        enriched_outputs = self._attach_observation_lineage(
            request,
            dict(outputs),
            evidence_payloads,
        )
        return AnalysisResult(
            result_id=result_id,
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs=enriched_outputs,
            evidence_ids=request.evidence_ids,
            execution_metadata={
                "executor": "MTS_V4.ExactMethodAnalysisExecutor",
                "execution_status": "SUCCESS",
            },
        )

    @classmethod
    def _attach_observation_lineage(
        cls,
        request: AnalysisRequest,
        outputs: dict[str, Any],
        evidence_payloads: Mapping[str, object],
    ) -> dict[str, Any]:
        """Attach hidden mechanical observation lineage without changing scientific columns.

        The exact Analysis implementation remains authoritative for calculations.
        This post-execution step records only which supplied input rows mechanically
        contributed to each reusable derived observation. It does not select inputs,
        variables, horizons, joins, or scientific meaning.
        """
        derived = outputs.get("derived_datasets")
        if not isinstance(derived, Mapping) or len(evidence_payloads) != 1:
            return outputs

        input_name = next(iter(evidence_payloads))
        method_id = request.method_id
        parameters = request.parameters

        if method_id == "analysis.transform.percent_change":
            dataset_name = "percent_change"
            lag = int(parameters["lag"])
            span = lambda row: (int(row["index"]) - lag, int(row["index"]), int(row["index"]))
        elif method_id == "analysis.rolling.statistics":
            dataset_name = "rolling_statistic"
            window = int(parameters["window"])
            span = lambda row: (int(row["index"]) - window + 1, int(row["index"]), int(row["index"]))
        elif method_id == "analysis.events.threshold":
            dataset_name = "threshold_events"
            span = lambda row: (int(row["index"]), int(row["index"]), int(row["index"]))
        elif method_id == "analysis.path.forward_measurement":
            dataset_name = "forward_path_observations"
            horizon = int(parameters["horizon"])
            span = lambda row: (int(row["index"]), int(row["index"]) + horizon, int(row["index"]))
        else:
            return outputs

        rows = derived.get(dataset_name)
        if not isinstance(rows, (list, tuple)):
            return outputs

        enriched_rows: list[Mapping[str, Any]] = []
        for raw_row in rows:
            if not isinstance(raw_row, Mapping) or "index" not in raw_row:
                enriched_rows.append(raw_row)
                continue
            start, end, anchor = span(raw_row)
            row = dict(raw_row)
            row["__observation_lineage"] = {
                "input_name": input_name,
                "input_row_start": start,
                "input_row_end": end,
                "input_row_anchor": anchor,
                "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
            }
            enriched_rows.append(row)

        derived_copy = dict(derived)
        derived_copy[dataset_name] = enriched_rows
        outputs["derived_datasets"] = derived_copy

        catalog = outputs.get("derived_dataset_catalog")
        if isinstance(catalog, Mapping) and isinstance(catalog.get(dataset_name), Mapping):
            catalog_copy = dict(catalog)
            entry = dict(catalog_copy[dataset_name])
            entry["observation_lineage"] = {
                "stored_in_rows_as": "__observation_lineage",
                "scientific_schema_unchanged": True,
                "meaning": (
                    "Campaign-local mechanical provenance identifying the supplied input name and "
                    "contributing input-row span/anchor for each derived observation."
                ),
            }
            catalog_copy[dataset_name] = entry
            outputs["derived_dataset_catalog"] = catalog_copy
        return outputs
