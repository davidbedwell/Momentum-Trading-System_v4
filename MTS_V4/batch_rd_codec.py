from __future__ import annotations

import json
from typing import Any, Mapping

from .batch_contracts import (
    BatchResearchDecision,
    ResearchPackageClosure,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from .contracts import Finding, ResearchPhase


class BatchResearchDecisionDecodeError(ValueError):
    pass


class BatchResearchDecisionCodec:
    """Strict representation codec for AI-authored batched scientific decisions."""

    @staticmethod
    def decode(text: str) -> BatchResearchDecision:
        raw = BatchResearchDecisionCodec._extract_json(text)
        if not isinstance(raw, Mapping):
            raise BatchResearchDecisionDecodeError("batch RD response must be a JSON object")

        continue_research = raw.get("continue_research")
        if not isinstance(continue_research, bool):
            raise BatchResearchDecisionDecodeError("continue_research must be boolean")

        packages_raw = raw.get("research_packages", [])
        if not isinstance(packages_raw, list):
            raise BatchResearchDecisionDecodeError("research_packages must be a list")
        packages = tuple(BatchResearchDecisionCodec._decode_package(item) for item in packages_raw)

        closures_raw = raw.get("rp_closures", [])
        if not isinstance(closures_raw, list):
            raise BatchResearchDecisionDecodeError("rp_closures must be a list")
        closures = tuple(BatchResearchDecisionCodec._decode_closure(item) for item in closures_raw)

        findings_raw = raw.get("promote_findings", [])
        if not isinstance(findings_raw, list):
            raise BatchResearchDecisionDecodeError("promote_findings must be a list")
        findings = tuple(BatchResearchDecisionCodec._decode_finding(item) for item in findings_raw)

        research_state = raw.get("research_state", {})
        if not isinstance(research_state, Mapping):
            raise BatchResearchDecisionDecodeError("research_state must be an object")

        close_reason = raw.get("close_reason")
        if close_reason is not None and not isinstance(close_reason, str):
            raise BatchResearchDecisionDecodeError("close_reason must be string or null")
        batch_interpretation = raw.get("batch_interpretation")
        if batch_interpretation is not None and not isinstance(batch_interpretation, str):
            raise BatchResearchDecisionDecodeError("batch_interpretation must be string or null")

        if continue_research and not packages:
            raise BatchResearchDecisionDecodeError(
                "continuing batched research requires at least one AI-authored Research Package"
            )
        if not continue_research and (not isinstance(close_reason, str) or not close_reason.strip()):
            raise BatchResearchDecisionDecodeError(
                "closing batched research requires a nonblank close_reason"
            )

        rp_ids = [package.rp_id for package in packages]
        if len(rp_ids) != len(set(rp_ids)):
            raise BatchResearchDecisionDecodeError(
                "research_packages rp_id values must be unique within a batch"
            )
        closure_ids = [closure.rp_id for closure in closures]
        if len(closure_ids) != len(set(closure_ids)):
            raise BatchResearchDecisionDecodeError("rp_closures rp_id values must be unique")
        analysis_ids = [analysis.analysis_id for package in packages for analysis in package.analyses]
        if len(analysis_ids) != len(set(analysis_ids)):
            raise BatchResearchDecisionDecodeError("analysis_id values must be unique across a batch")

        return BatchResearchDecision(
            continue_research=continue_research,
            research_packages=packages,
            rp_closures=closures,
            promote_findings=findings,
            research_state=dict(research_state),
            close_reason=close_reason,
            batch_interpretation=batch_interpretation,
        )

    @staticmethod
    def _decode_package(raw: Any) -> ResearchPackagePlan:
        if not isinstance(raw, Mapping):
            raise BatchResearchDecisionDecodeError("each research_packages entry must be an object")
        rp_id = BatchResearchDecisionCodec._nonblank(raw.get("rp_id"), "rp_id")
        objective = BatchResearchDecisionCodec._nonblank(raw.get("objective"), "objective")
        parent_rp_id = raw.get("parent_rp_id")
        if parent_rp_id is not None:
            parent_rp_id = BatchResearchDecisionCodec._nonblank(parent_rp_id, "parent_rp_id")
            if parent_rp_id == rp_id:
                raise BatchResearchDecisionDecodeError("Research Package cannot name itself as parent_rp_id")
        decision_boundary = raw.get("decision_boundary")
        if decision_boundary is not None and not isinstance(decision_boundary, str):
            raise BatchResearchDecisionDecodeError("decision_boundary must be string or null")
        analyses_raw = raw.get("analyses")
        if not isinstance(analyses_raw, list) or not analyses_raw:
            raise BatchResearchDecisionDecodeError("each Research Package must contain at least one analysis")
        analyses = tuple(
            BatchResearchDecisionCodec._decode_analysis(item, package_rp_id=rp_id)
            for item in analyses_raw
        )
        return ResearchPackagePlan(
            rp_id=rp_id,
            objective=objective,
            analyses=analyses,
            parent_rp_id=parent_rp_id,
            decision_boundary=decision_boundary,
        )

    @staticmethod
    def _decode_closure(raw: Any) -> ResearchPackageClosure:
        if not isinstance(raw, Mapping):
            raise BatchResearchDecisionDecodeError("each rp_closures entry must be an object")
        rp_id = BatchResearchDecisionCodec._nonblank(raw.get("rp_id"), "rp_closures.rp_id")
        close_reason = BatchResearchDecisionCodec._nonblank(
            raw.get("close_reason"), "rp_closures.close_reason"
        )
        final_assessment = raw.get("final_assessment")
        if final_assessment is not None and not isinstance(final_assessment, str):
            raise BatchResearchDecisionDecodeError(
                "rp_closures.final_assessment must be string or null"
            )
        return ResearchPackageClosure(
            rp_id=rp_id,
            close_reason=close_reason,
            final_assessment=final_assessment,
        )

    @staticmethod
    def _decode_analysis(raw: Any, *, package_rp_id: str) -> ScientificAnalysisSpecification:
        if not isinstance(raw, Mapping):
            raise BatchResearchDecisionDecodeError("each analyses entry must be an object")
        analysis_id = BatchResearchDecisionCodec._nonblank(raw.get("analysis_id"), "analysis_id")
        rp_id = BatchResearchDecisionCodec._nonblank(raw.get("rp_id", package_rp_id), "analysis.rp_id")
        if rp_id != package_rp_id:
            raise BatchResearchDecisionDecodeError(
                f"analysis {analysis_id!r} rp_id must equal containing Research Package {package_rp_id!r}"
            )
        question_id = BatchResearchDecisionCodec._nonblank(raw.get("question_id"), "question_id")
        subject_id = BatchResearchDecisionCodec._nonblank(raw.get("subject_id"), "subject_id")
        question = BatchResearchDecisionCodec._nonblank(raw.get("question"), "question")
        method_id = BatchResearchDecisionCodec._nonblank(raw.get("method_id"), "method_id")
        rationale = raw.get("rationale", "")
        if not isinstance(rationale, str):
            raise BatchResearchDecisionDecodeError("rationale must be a string")

        parent_question_id = raw.get("parent_question_id")
        if parent_question_id is not None:
            parent_question_id = BatchResearchDecisionCodec._nonblank(
                parent_question_id, "parent_question_id"
            )
            if parent_question_id == question_id:
                raise BatchResearchDecisionDecodeError("question cannot name itself as parent_question_id")
        parent_rp_id = raw.get("parent_rp_id")
        if parent_rp_id is not None:
            parent_rp_id = BatchResearchDecisionCodec._nonblank(parent_rp_id, "analysis.parent_rp_id")
            if parent_rp_id == rp_id:
                raise BatchResearchDecisionDecodeError("analysis parent_rp_id cannot equal rp_id")

        inputs_raw = raw.get("inputs", [])
        if not isinstance(inputs_raw, list):
            raise BatchResearchDecisionDecodeError("inputs must be a list")
        inputs = tuple(BatchResearchDecisionCodec._decode_input(item) for item in inputs_raw)

        parameters = raw.get("parameters")
        if not isinstance(parameters, Mapping):
            raise BatchResearchDecisionDecodeError("parameters must be an object")
        try:
            phase = ResearchPhase(str(raw.get("research_phase")))
        except ValueError as exc:
            raise BatchResearchDecisionDecodeError(
                "research_phase must be EXPLORATION or VALIDATION"
            ) from exc

        return ScientificAnalysisSpecification(
            analysis_id=analysis_id,
            rp_id=rp_id,
            question_id=question_id,
            subject_id=subject_id,
            question=question,
            method_id=method_id,
            inputs=inputs,
            parameters=dict(parameters),
            research_phase=phase,
            rationale=rationale,
            parent_question_id=parent_question_id,
            parent_rp_id=parent_rp_id,
        )

    @staticmethod
    def _decode_input(raw: Any) -> ScientificInputReference:
        if not isinstance(raw, Mapping):
            raise BatchResearchDecisionDecodeError("each inputs entry must be an object")
        role = BatchResearchDecisionCodec._nonblank(raw.get("role"), "input.role")
        evidence_id = raw.get("evidence_id")
        analysis_id = raw.get("analysis_id")
        dataset_name = raw.get("dataset_name")
        if evidence_id is not None:
            evidence_id = BatchResearchDecisionCodec._nonblank(evidence_id, "input.evidence_id")
        if analysis_id is not None:
            analysis_id = BatchResearchDecisionCodec._nonblank(analysis_id, "input.analysis_id")
        if dataset_name is not None:
            dataset_name = BatchResearchDecisionCodec._nonblank(dataset_name, "input.dataset_name")
        if (evidence_id is None) == (analysis_id is None):
            raise BatchResearchDecisionDecodeError(
                f"input role {role!r} must provide exactly one of evidence_id or analysis_id"
            )
        if evidence_id is not None and dataset_name is not None:
            raise BatchResearchDecisionDecodeError(
                f"input role {role!r} cannot use dataset_name with acquired evidence"
            )
        return ScientificInputReference(
            role=role,
            evidence_id=evidence_id,
            analysis_id=analysis_id,
            dataset_name=dataset_name,
        )

    @staticmethod
    def _decode_finding(raw: Any) -> Finding:
        if not isinstance(raw, Mapping):
            raise BatchResearchDecisionDecodeError("each promoted finding must be an object")
        required = (
            "finding_id",
            "subject_id",
            "statement",
            "supporting_result_ids",
            "evidence_ids",
        )
        missing = [key for key in required if key not in raw]
        if missing:
            raise BatchResearchDecisionDecodeError(f"finding missing required fields: {missing}")
        supporting = raw["supporting_result_ids"]
        evidence = raw["evidence_ids"]
        metadata = raw.get("metadata", {})
        if not isinstance(supporting, list) or not all(isinstance(item, str) for item in supporting):
            raise BatchResearchDecisionDecodeError("supporting_result_ids must be a list of strings")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise BatchResearchDecisionDecodeError("finding evidence_ids must be a list of strings")
        if not isinstance(metadata, Mapping):
            raise BatchResearchDecisionDecodeError("finding metadata must be an object")
        return Finding(
            finding_id=str(raw["finding_id"]),
            subject_id=str(raw["subject_id"]),
            statement=str(raw["statement"]),
            supporting_result_ids=tuple(supporting),
            evidence_ids=tuple(evidence),
            metadata=dict(metadata),
        )

    @staticmethod
    def _nonblank(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise BatchResearchDecisionDecodeError(f"{field} must be a nonblank string")
        return value

    @staticmethod
    def _extract_json(text: str) -> Any:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise BatchResearchDecisionDecodeError(f"invalid batch decision JSON: {exc}") from exc
