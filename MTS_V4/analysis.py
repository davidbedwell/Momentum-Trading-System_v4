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
    substitution path in this executor.
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

        try:
            outputs = registered.implementation(evidence_payloads, request.parameters)
        except Exception as exc:
            raise AnalysisExecutionError(
                f"analysis method {request.method_id} failed: {type(exc).__name__}: {exc}"
            ) from exc

        if not isinstance(outputs, Mapping):
            raise AnalysisExecutionError(
                f"analysis method {request.method_id} must return a mapping"
            )

        self._sequence += 1
        return AnalysisResult(
            result_id=f"analysis-result:{self._sequence}",
            request_id=request.request_id,
            subject_id=request.subject_id,
            method_id=request.method_id,
            outputs=dict(outputs),
            evidence_ids=request.evidence_ids,
            execution_metadata={"executor": "MTS_V4.ExactMethodAnalysisExecutor"},
        )
