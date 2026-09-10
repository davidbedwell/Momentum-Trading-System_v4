from __future__ import annotations

from collections.abc import Mapping as ABCMapping, Sequence, Sized
from typing import Any, Mapping

from .contracts import AnalysisRequest, AnalysisResult, AnalysisResultInput, ContractDefect, EvidenceDescriptor, ResearchPhase
from .method_catalog import MethodCatalog, MethodNotFoundError, ParameterContract


class ObjectiveContractValidator:
    """Validate only objective execution contracts.

    This class must never select a method, rewrite a scientific question,
    invent a parameter value, choose a prior Analysis output, or judge
    scientific merit.
    """

    def __init__(self, catalog: MethodCatalog) -> None:
        self._catalog = catalog

    def validate(
        self,
        request: AnalysisRequest,
        evidence: Mapping[str, EvidenceDescriptor],
        analysis_results: Mapping[str, AnalysisResult] | None = None,
    ) -> tuple[ContractDefect, ...]:
        defects: list[ContractDefect] = []
        prior_results = analysis_results or {}

        try:
            spec = self._catalog.get(request.method_id)
        except MethodNotFoundError:
            return (
                ContractDefect(
                    code="MISSING_CAPABILITY",
                    message=f"Unknown analysis method: {request.method_id}",
                    field="method_id",
                    method_id=request.method_id,
                ),
            )

        if request.research_phase is ResearchPhase.EXPLORATION and not spec.exploration_allowed:
            defects.append(
                ContractDefect(
                    code="INVALID_RESEARCH_PHASE",
                    message=f"{spec.method_id} is not executable in EXPLORATION",
                    field="research_phase",
                    method_id=spec.method_id,
                )
            )
        if request.research_phase is ResearchPhase.VALIDATION and not spec.validation_allowed:
            defects.append(
                ContractDefect(
                    code="INVALID_RESEARCH_PHASE",
                    message=f"{spec.method_id} is not executable in VALIDATION",
                    field="research_phase",
                    method_id=spec.method_id,
                )
            )
        if request.research_phase is ResearchPhase.VALIDATION and spec.allows_future_information:
            defects.append(
                ContractDefect(
                    code="TEMPORAL_CONTRACT_VIOLATION",
                    message=f"{spec.method_id} permits future information and cannot execute in VALIDATION",
                    field="research_phase",
                    method_id=spec.method_id,
                )
            )

        resolved: list[EvidenceDescriptor] = []
        for evidence_id in request.evidence_ids:
            item = evidence.get(evidence_id)
            if item is None:
                if str(evidence_id).startswith("analysis-result:"):
                    message = (
                        f"Evidence reference does not exist in the active campaign runtime: {evidence_id}. "
                        "Do not reuse this unavailable identifier in the repaired request. analysis-result IDs "
                        "are not evidence_ids; prior Analysis outputs must be referenced through analysis_inputs "
                        "using an exact result_id that is currently available in the active campaign runtime and "
                        "an exact output_path. If acquired evidence is required, use an exact currently advertised "
                        "evidence_id from the active evidence inventory if scientifically appropriate. Deterministic "
                        "code will not select a replacement or scientific direction."
                    )
                else:
                    message = (
                        f"Evidence reference does not exist in the active campaign runtime: {evidence_id}. "
                        "Do not reuse this unavailable evidence_id in the repaired request. If the same scientific "
                        "work is still desired, select an exact currently advertised evidence_id from the active "
                        "evidence inventory if scientifically appropriate, or choose another scientific direction. "
                        "Deterministic code will not select a replacement or scientific direction."
                    )
                defects.append(
                    ContractDefect(
                        code="MISSING_EVIDENCE",
                        message=message,
                        field="evidence_ids",
                        method_id=spec.method_id,
                    )
                )
                continue
            if item.subject_id != request.subject_id:
                defects.append(
                    ContractDefect(
                        code="LINEAGE_MISMATCH",
                        message=(
                            f"Evidence {evidence_id} belongs to {item.subject_id}, "
                            f"not request subject {request.subject_id}"
                        ),
                        field="evidence_ids",
                        method_id=spec.method_id,
                    )
                )
            resolved.append(item)

        input_names: set[str] = set()
        for reference in request.analysis_inputs:
            defects.extend(
                self._validate_analysis_input(
                    request=request,
                    reference=reference,
                    prior_results=prior_results,
                    input_names=input_names,
                )
            )
            input_names.add(reference.input_name)

        if resolved and spec.artifact_types:
            incompatible = [
                item.evidence_id
                for item in resolved
                if item.artifact_type not in spec.artifact_types
            ]
            if incompatible:
                defects.append(
                    ContractDefect(
                        code="INVALID_SCOPE",
                        message=(
                            f"{spec.method_id} requires artifact type in {spec.artifact_types}; "
                            f"incompatible evidence: {tuple(incompatible)}"
                        ),
                        field="evidence_ids",
                        method_id=spec.method_id,
                    )
                )

        known_rows = [item.row_count for item in resolved if item.row_count is not None]
        if spec.minimum_sample and known_rows and max(known_rows) < spec.minimum_sample:
            defects.append(
                ContractDefect(
                    code="INSUFFICIENT_SAMPLE",
                    message=(
                        f"{spec.method_id} requires at least {spec.minimum_sample} rows; "
                        f"largest supplied evidence has {max(known_rows)}"
                    ),
                    field="evidence_ids",
                    method_id=spec.method_id,
                )
            )

        for contract in spec.parameters:
            defects.extend(self._validate_parameter(request, contract))

        return tuple(defects)

    @classmethod
    def _validate_analysis_input(
        cls,
        *,
        request: AnalysisRequest,
        reference: AnalysisResultInput,
        prior_results: Mapping[str, AnalysisResult],
        input_names: set[str],
    ) -> tuple[ContractDefect, ...]:
        defects: list[ContractDefect] = []
        if not reference.input_name.strip():
            defects.append(
                ContractDefect(
                    code="INVALID_ANALYSIS_INPUT",
                    message="analysis input input_name cannot be blank",
                    field="analysis_inputs",
                    method_id=request.method_id,
                )
            )
        if reference.input_name in input_names:
            defects.append(
                ContractDefect(
                    code="DUPLICATE_ANALYSIS_INPUT_NAME",
                    message=f"analysis input name is duplicated: {reference.input_name}",
                    field="analysis_inputs",
                    method_id=request.method_id,
                )
            )
        result = prior_results.get(reference.result_id)
        if result is None:
            defects.append(
                ContractDefect(
                    code="MISSING_ANALYSIS_RESULT",
                    message=(
                        f"Prior Analysis result payload is unavailable in the active campaign runtime: "
                        f"{reference.result_id}. Do not reference this unavailable result_id again in "
                        "analysis_inputs of the repaired request. If the same scientific work is still desired, "
                        "the Research Director may reconstruct or regenerate the needed intermediate result by "
                        "issuing a new executable Analysis request from currently available evidence or other "
                        "currently available Analysis outputs, or may choose another scientific direction. "
                        "A regenerated execution requires its own new request_id. Deterministic code will not "
                        "select the replacement inputs, method, parameters, or scientific direction."
                    ),
                    field="analysis_inputs",
                    method_id=request.method_id,
                )
            )
            return tuple(defects)
        if result.subject_id != request.subject_id:
            defects.append(
                ContractDefect(
                    code="LINEAGE_MISMATCH",
                    message=(
                        f"Analysis result {reference.result_id} belongs to {result.subject_id}, "
                        f"not request subject {request.subject_id}"
                    ),
                    field="analysis_inputs",
                    method_id=request.method_id,
                )
            )
            return tuple(defects)
        try:
            cls.resolve_analysis_input(reference, result)
        except (KeyError, IndexError, TypeError) as exc:
            execution_status = result.execution_metadata.get("execution_status")
            if execution_status == "ERROR":
                message = (
                    f"Analysis result {reference.result_id} has execution_status=ERROR and does not "
                    f"contain the requested output_path {reference.output_path}: "
                    f"{type(exc).__name__}: {exc}. This failed result cannot supply that analysis input. "
                    "The Research Director may regenerate the needed result, choose another successful "
                    "prior Analysis result and use an exact advertised derived_dataset_catalog output_path, "
                    "use acquired evidence directly if the selected method permits, or pursue another "
                    "scientific direction. Deterministic code will not choose among those options."
                )
            else:
                message = (
                    f"Analysis result {reference.result_id} does not contain the requested "
                    f"output_path {reference.output_path}: {type(exc).__name__}: {exc}"
                )
            defects.append(
                ContractDefect(
                    code="MISSING_ANALYSIS_OUTPUT",
                    message=message,
                    field="analysis_inputs",
                    method_id=request.method_id,
                )
            )
        return tuple(defects)

    @staticmethod
    def resolve_analysis_input(reference: AnalysisResultInput, result: AnalysisResult) -> object:
        value: object = result.outputs
        for component in reference.output_path:
            if isinstance(component, str):
                if not isinstance(value, ABCMapping):
                    raise TypeError(f"cannot select key {component!r} from {type(value).__name__}")
                value = value[component]
            else:
                if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
                    raise TypeError(f"cannot select index {component} from {type(value).__name__}")
                value = value[component]
        return value

    @staticmethod
    def _validate_parameter(
        request: AnalysisRequest,
        contract: ParameterContract,
    ) -> tuple[ContractDefect, ...]:
        if contract.name not in request.parameters:
            if contract.required:
                return (
                    ContractDefect(
                        code="MISSING_SPECIFICATION",
                        message=(
                            f"{request.method_id} requires parameter {contract.name}"
                        ),
                        field=contract.name,
                        method_id=request.method_id,
                    ),
                )
            return ()

        value = request.parameters[contract.name]
        defects: list[ContractDefect] = []

        if contract.python_types and not isinstance(value, contract.python_types):
            expected = ", ".join(t.__name__ for t in contract.python_types)
            defects.append(
                ContractDefect(
                    code="INVALID_PARAMETER_TYPE",
                    message=(
                        f"{request.method_id} parameter {contract.name} requires type "
                        f"{expected}; received {type(value).__name__}"
                    ),
                    field=contract.name,
                    method_id=request.method_id,
                )
            )
            return tuple(defects)

        if isinstance(value, Sized) and not isinstance(value, (str, bytes)):
            length = len(value)
            if contract.exact_length is not None and length != contract.exact_length:
                defects.append(
                    ContractDefect(
                        code="INVALID_PARAMETER_CARDINALITY",
                        message=(
                            f"{request.method_id} parameter {contract.name} requires exactly "
                            f"{contract.exact_length} values; received {length}"
                        ),
                        field=contract.name,
                        method_id=request.method_id,
                    )
                )
            if contract.minimum_length is not None and length < contract.minimum_length:
                defects.append(
                    ContractDefect(
                        code="INVALID_PARAMETER_CARDINALITY",
                        message=(
                            f"{request.method_id} parameter {contract.name} requires at least "
                            f"{contract.minimum_length} values; received {length}"
                        ),
                        field=contract.name,
                        method_id=request.method_id,
                    )
                )
            if contract.maximum_length is not None and length > contract.maximum_length:
                defects.append(
                    ContractDefect(
                        code="INVALID_PARAMETER_CARDINALITY",
                        message=(
                            f"{request.method_id} parameter {contract.name} allows at most "
                            f"{contract.maximum_length} values; received {length}"
                        ),
                        field=contract.name,
                        method_id=request.method_id,
                    )
                )

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if contract.minimum_value is not None and value < contract.minimum_value:
                defects.append(
                    ContractDefect(
                        code="INVALID_PARAMETER_RANGE",
                        message=(
                            f"{request.method_id} parameter {contract.name} must be >= "
                            f"{contract.minimum_value}; received {value}"
                        ),
                        field=contract.name,
                        method_id=request.method_id,
                    )
                )
            if contract.maximum_value is not None and value > contract.maximum_value:
                defects.append(
                    ContractDefect(
                        code="INVALID_PARAMETER_RANGE",
                        message=(
                            f"{request.method_id} parameter {contract.name} must be <= "
                            f"{contract.maximum_value}; received {value}"
                        ),
                        field=contract.name,
                        method_id=request.method_id,
                    )
                )

        if contract.allowed_values and value not in contract.allowed_values:
            defects.append(
                ContractDefect(
                    code="INVALID_PARAMETER_VALUE",
                    message=(
                        f"{request.method_id} parameter {contract.name} must be one of "
                        f"{contract.allowed_values}; received {value!r}"
                    ),
                    field=contract.name,
                    method_id=request.method_id,
                )
            )

        return tuple(defects)
