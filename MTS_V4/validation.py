from __future__ import annotations

from collections.abc import Sized
from typing import Mapping

from .contracts import AnalysisRequest, ContractDefect, EvidenceDescriptor, ResearchPhase
from .method_catalog import MethodCatalog, MethodNotFoundError, ParameterContract


class ObjectiveContractValidator:
    """Validate only objective execution contracts.

    This class must never select a method, rewrite a scientific question,
    invent a parameter value, or judge scientific merit.
    """

    def __init__(self, catalog: MethodCatalog) -> None:
        self._catalog = catalog

    def validate(
        self,
        request: AnalysisRequest,
        evidence: Mapping[str, EvidenceDescriptor],
    ) -> tuple[ContractDefect, ...]:
        defects: list[ContractDefect] = []

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
                defects.append(
                    ContractDefect(
                        code="MISSING_EVIDENCE",
                        message=f"Evidence reference does not exist: {evidence_id}",
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
