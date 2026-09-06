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

        return AnalysisResult(
            result_id=result_id,
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs=dict(outputs),
            evidence_ids=request.evidence_ids,
            execution_metadata={
                "executor": "MTS_V4.ExactMethodAnalysisExecutor",
                "execution_status": "SUCCESS",
            },
        )
