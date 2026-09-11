from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from uuid import uuid4

from .batch_contracts import CompiledAnalysis, ScientificAnalysisSpecification
from .contracts import AnalysisRequest, AnalysisResult, AnalysisResultInput, EvidenceDescriptor


class BatchCompilationError(RuntimeError):
    """Objective compiler defect that cannot be resolved without AI scientific choice."""


@dataclass(frozen=True, slots=True)
class BatchCompilerContext:
    evidence: Mapping[str, EvidenceDescriptor]
    results_by_analysis_id: Mapping[str, AnalysisResult]


def _safe_binding_name(role: str, ordinal: int, occupied: set[str]) -> str:
    base = re.sub(r"[^A-Za-z0-9_]+", "_", role.strip()).strip("_").lower() or "input"
    candidate = f"input_{ordinal}_{base}"
    suffix = 2
    while candidate in occupied:
        candidate = f"input_{ordinal}_{base}_{suffix}"
        suffix += 1
    occupied.add(candidate)
    return candidate


def _rewrite_input_roles(value: Any, role_bindings: Mapping[str, str]) -> Any:
    """Replace only executor input_name fields; all scientific values remain untouched."""
    if isinstance(value, Mapping):
        rewritten: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if key == "input_name" and isinstance(raw_value, str) and raw_value in role_bindings:
                rewritten[key] = role_bindings[raw_value]
            else:
                rewritten[key] = _rewrite_input_roles(raw_value, role_bindings)
        return rewritten
    if isinstance(value, list):
        return [_rewrite_input_roles(item, role_bindings) for item in value]
    if isinstance(value, tuple):
        return tuple(_rewrite_input_roles(item, role_bindings) for item in value)
    return value


def _resolve_reusable_dataset(
    *,
    source_analysis_id: str,
    source_result: AnalysisResult,
    dataset_name: str | None,
) -> tuple[tuple[str | int, ...], str]:
    if source_result.execution_metadata.get("execution_status") != "SUCCESS":
        raise BatchCompilationError(
            f"prior analysis {source_analysis_id!r} did not execute successfully and cannot supply a reusable dataset"
        )
    raw_catalog = source_result.outputs.get("derived_dataset_catalog")
    if not isinstance(raw_catalog, Mapping) or not raw_catalog:
        raise BatchCompilationError(
            f"prior analysis {source_analysis_id!r} exposes no reusable derived dataset"
        )
    candidates = {
        str(name): metadata
        for name, metadata in raw_catalog.items()
        if isinstance(metadata, Mapping)
        and isinstance(metadata.get("output_path"), (list, tuple))
    }
    if not candidates:
        raise BatchCompilationError(
            f"prior analysis {source_analysis_id!r} exposes no reusable dataset with an advertised output_path"
        )
    if dataset_name is None:
        if len(candidates) != 1:
            raise BatchCompilationError(
                "AMBIGUOUS_SCIENTIFIC_REPAIR_REQUIRED: prior analysis "
                f"{source_analysis_id!r} exposes multiple reusable datasets {tuple(candidates)}; "
                "RD must identify the scientifically intended dataset_name"
            )
        selected_name = next(iter(candidates))
    else:
        selected_name = dataset_name
        if selected_name not in candidates:
            raise BatchCompilationError(
                f"prior analysis {source_analysis_id!r} does not advertise reusable dataset {selected_name!r}; "
                f"available datasets are {tuple(candidates)}"
            )
    output_path = tuple(candidates[selected_name]["output_path"])
    if not output_path:
        raise BatchCompilationError(
            f"reusable dataset {selected_name!r} from {source_analysis_id!r} has an empty output_path"
        )
    return output_path, selected_name


class ScientificSpecificationCompiler:
    """Compile AI scientific intent into exact AnalysisRequest plumbing.

    The compiler resolves only machine identities and role bindings. It does not
    select evidence, methods, variables, parameters, horizons, joins, hypotheses,
    or follow-up science.
    """

    def compile(
        self,
        specification: ScientificAnalysisSpecification,
        *,
        context: BatchCompilerContext,
    ) -> CompiledAnalysis:
        if not specification.analysis_id.strip():
            raise BatchCompilationError("analysis_id cannot be blank")
        if not specification.rp_id.strip():
            raise BatchCompilationError("rp_id cannot be blank")
        if not specification.question_id.strip():
            raise BatchCompilationError("question_id cannot be blank")

        roles = [reference.role for reference in specification.inputs]
        if any(not role.strip() for role in roles):
            raise BatchCompilationError("scientific input role cannot be blank")
        if len(roles) != len(set(roles)):
            raise BatchCompilationError(
                f"scientific input roles must be unique within {specification.analysis_id!r}: {tuple(roles)}"
            )

        evidence_ids: list[str] = []
        analysis_inputs: list[AnalysisResultInput] = []
        occupied = set(context.evidence)
        role_bindings: dict[str, str] = {}
        repairs: list[str] = []

        for ordinal, reference in enumerate(specification.inputs, start=1):
            has_evidence = reference.evidence_id is not None
            has_analysis = reference.analysis_id is not None
            if has_evidence == has_analysis:
                raise BatchCompilationError(
                    f"input role {reference.role!r} must identify exactly one source: evidence_id or analysis_id"
                )
            binding = _safe_binding_name(reference.role, ordinal, occupied)
            role_bindings[reference.role] = binding

            if has_evidence:
                assert reference.evidence_id is not None
                descriptor = context.evidence.get(reference.evidence_id)
                if descriptor is None:
                    raise BatchCompilationError(
                        f"scientifically selected evidence_id is unavailable: {reference.evidence_id}"
                    )
                if descriptor.subject_id != specification.subject_id:
                    raise BatchCompilationError(
                        f"evidence {reference.evidence_id} belongs to {descriptor.subject_id}, not {specification.subject_id}"
                    )
                evidence_ids.append(reference.evidence_id)
                role_bindings[reference.role] = reference.evidence_id
                continue

            assert reference.analysis_id is not None
            source_result = context.results_by_analysis_id.get(reference.analysis_id)
            if source_result is None:
                raise BatchCompilationError(
                    f"dependency {reference.analysis_id!r} has not produced a result"
                )
            if source_result.subject_id != specification.subject_id:
                raise BatchCompilationError(
                    f"dependency {reference.analysis_id!r} belongs to another subject: {source_result.subject_id}"
                )
            output_path, selected_name = _resolve_reusable_dataset(
                source_analysis_id=reference.analysis_id,
                source_result=source_result,
                dataset_name=reference.dataset_name,
            )
            if reference.dataset_name is None:
                repairs.append(
                    f"resolved sole reusable dataset {selected_name!r} from logical dependency {reference.analysis_id!r}"
                )
            analysis_inputs.append(
                AnalysisResultInput(
                    result_id=source_result.result_id,
                    output_path=output_path,
                    input_name=binding,
                )
            )

        compiled_parameters = _rewrite_input_roles(specification.parameters, role_bindings)
        request = AnalysisRequest(
            request_id=f"batch-request:{uuid4().hex}",
            subject_id=specification.subject_id,
            question=specification.question,
            method_id=specification.method_id,
            evidence_ids=tuple(dict.fromkeys(evidence_ids)),
            parameters=compiled_parameters,
            research_phase=specification.research_phase,
            rationale=specification.rationale,
            analysis_inputs=tuple(analysis_inputs),
            rp_id=specification.rp_id,
            question_id=specification.question_id,
            parent_question_id=specification.parent_question_id,
            parent_rp_id=specification.parent_rp_id,
        )
        return CompiledAnalysis(
            analysis_id=specification.analysis_id,
            rp_id=specification.rp_id,
            request=request,
            binding_map=dict(role_bindings),
            mechanical_repairs=tuple(repairs),
        )


def topological_analysis_order(
    specifications: Sequence[ScientificAnalysisSpecification],
    *,
    available_analysis_ids: Sequence[str] = (),
) -> tuple[ScientificAnalysisSpecification, ...]:
    """Order exact AI-authored dependencies, allowing prior completed batch results."""
    by_id = {item.analysis_id: item for item in specifications}
    if len(by_id) != len(specifications):
        raise BatchCompilationError("analysis_id values must be unique across one batch")
    prior_ids = set(available_analysis_ids)
    reused = sorted(set(by_id).intersection(prior_ids))
    if reused:
        raise BatchCompilationError(
            f"new batch reuses already completed analysis_id values: {tuple(reused)}"
        )

    dependencies: dict[str, set[str]] = {}
    for item in specifications:
        all_deps = {
            ref.analysis_id
            for ref in item.inputs
            if ref.analysis_id is not None
        }
        unknown = sorted(dep for dep in all_deps if dep not in by_id and dep not in prior_ids)
        if unknown:
            raise BatchCompilationError(
                f"analysis {item.analysis_id!r} references unknown logical dependencies: {tuple(unknown)}"
            )
        if item.analysis_id in all_deps:
            raise BatchCompilationError(f"analysis {item.analysis_id!r} cannot depend on itself")
        dependencies[item.analysis_id] = {dep for dep in all_deps if dep in by_id}

    ordered: list[ScientificAnalysisSpecification] = []
    remaining = dict(dependencies)
    while remaining:
        ready = [
            analysis_id
            for analysis_id in by_id
            if analysis_id in remaining and not remaining[analysis_id]
        ]
        if not ready:
            raise BatchCompilationError(
                "batch Analysis dependency graph contains a cycle; RD must revise the scientific dependency structure"
            )
        for analysis_id in ready:
            ordered.append(by_id[analysis_id])
            remaining.pop(analysis_id)
            for deps in remaining.values():
                deps.discard(analysis_id)
    return tuple(ordered)
