from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from enum import Enum
from typing import Any, Mapping, Sequence

from .contracts import AnalysisRequest, AnalysisResult, ContractDefect, EvidenceDescriptor, ResearchDecision, SubjectMetadata
from .rd_codec import ResearchDecisionCodec


class ResearchDirectorTransportError(RuntimeError):
    pass


class OpenAICompatibleResearchDirector:
    """OpenAI-compatible transport for the v4 AI Research Director.

    Configuration is environment-driven so credentials and endpoint details are
    deferred to integration time and never embedded in source control.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        self._base_url = (base_url or os.getenv("MTS_RD_BASE_URL") or "").rstrip("/")
        self._model = model or os.getenv("MTS_RD_MODEL") or ""
        self._api_key = api_key if api_key is not None else os.getenv("MTS_RD_API_KEY", "")
        self._timeout_seconds = timeout_seconds
        if not self._base_url:
            raise ValueError("MTS_RD_BASE_URL or base_url is required")
        if not self._model:
            raise ValueError("MTS_RD_MODEL or model is required")

    def begin_research(self, *, mission: str, subject: SubjectMetadata, evidence: Sequence[EvidenceDescriptor], available_methods: Sequence[Mapping[str, Any]], nexus_context: Mapping[str, object]) -> ResearchDecision:
        return self._request_decision(operation="BEGIN_RESEARCH", mission=mission, payload={"subject": asdict(subject), "evidence": [asdict(item) for item in evidence], "available_analysis_methods": self._json_safe(available_methods), "objective_execution_requirements": self._execution_requirements(evidence=evidence, available_methods=available_methods), "nexus_context": self._json_safe(nexus_context)})

    def resume_research(self, *, mission: str, subject: SubjectMetadata, prior_decision: ResearchDecision, evidence_continuity: Mapping[str, object], evidence: Sequence[EvidenceDescriptor], available_methods: Sequence[Mapping[str, Any]], nexus_context: Mapping[str, object]) -> ResearchDecision:
        return self._request_decision(operation="RESUME_RESEARCH", mission=mission, payload={"subject": asdict(subject), "prior_decision": self._json_safe(asdict(prior_decision)), "evidence_continuity": self._json_safe(evidence_continuity), "evidence": [asdict(item) for item in evidence], "available_analysis_methods": self._json_safe(available_methods), "objective_execution_requirements": self._execution_requirements(evidence=evidence, available_methods=available_methods), "nexus_context": self._json_safe(nexus_context)})

    def repair_request(self, *, mission: str, subject: SubjectMetadata, prior_decision: ResearchDecision, defects: Sequence[ContractDefect], evidence: Sequence[EvidenceDescriptor], available_methods: Sequence[Mapping[str, Any]], nexus_context: Mapping[str, object]) -> ResearchDecision:
        return self._request_decision(operation="REPAIR_OBJECTIVE_CONTRACT", mission=mission, payload={"subject": asdict(subject), "prior_decision": self._json_safe(asdict(prior_decision)), "objective_contract_defects": [asdict(item) for item in defects], "evidence": [asdict(item) for item in evidence], "available_analysis_methods": self._json_safe(available_methods), "objective_execution_requirements": self._execution_requirements(evidence=evidence, available_methods=available_methods), "nexus_context": self._json_safe(nexus_context)})

    def interpret_result(self, *, mission: str, subject: SubjectMetadata, request: AnalysisRequest, result: AnalysisResult, evidence: Sequence[EvidenceDescriptor], available_methods: Sequence[Mapping[str, Any]], nexus_context: Mapping[str, object]) -> ResearchDecision:
        return self._request_decision(operation="INTERPRET_ANALYSIS_RESULT", mission=mission, payload={"subject": asdict(subject), "analysis_request": self._json_safe(asdict(request)), "analysis_result": self._json_safe(asdict(result)), "evidence": [asdict(item) for item in evidence], "available_analysis_methods": self._json_safe(available_methods), "objective_execution_requirements": self._execution_requirements(evidence=evidence, available_methods=available_methods), "nexus_context": self._json_safe(nexus_context)})

    @classmethod
    def _execution_requirements(cls, *, evidence: Sequence[EvidenceDescriptor], available_methods: Sequence[Mapping[str, Any]]) -> Mapping[str, object]:
        """Publish every deterministic condition RD can be held to."""
        return {
            "visibility_rule": "Any deterministic requirement that can reject or block an AI Research Director request or finding must be disclosed to the Research Director before the request or finding is judged against it.",
            "analysis_request": {
                "method_id": "must identify an available_analysis_methods entry exactly",
                "subject_id": "must equal the active subject_id",
                "evidence_ids": "must identify supplied raw evidence exactly; may be empty when execution uses only explicit analysis_inputs",
                "analysis_inputs": (
                    "optional explicit references to prior campaign-local Analysis outputs. Each entry "
                    "must supply result_id, exact output_path, and input_name. Deterministic code may "
                    "resolve only the exact RD-authored reference and may not choose or substitute a "
                    "prior result or output. Prior derived outputs are temporary and are not persisted "
                    "through process restart; an unavailable result is returned as an objective defect "
                    "so RD may decide whether to regenerate it."
                ),
                "method_contracts": cls._json_safe(available_methods),
                "no_hidden_defaults": "Scientifically meaningful missing parameters are not inferred, defaulted, or substituted by deterministic code.",
            },
            "finding_envelope": {
                "closed_required_fields": ["finding_id", "subject_id", "statement", "supporting_result_ids", "evidence_ids"],
                "metadata": "open-ended object authored by RD; arbitrary scientific labels, nested structures, classifications, applicability, limitations, relationships, confidence judgments, or previously unanticipated concepts are permitted",
                "scientific_taxonomy_is_open": True,
                "deterministic_scientific_veto": False,
                "meaning": "Deterministic code may validate only representation, identity, and lineage. It may not reject a finding because its scientific conclusion, category, label, or metadata was not anticipated by code.",
            },
            "available_evidence": [
                {
                    "evidence_id": item.evidence_id,
                    "subject_id": item.subject_id,
                    "evidence_type": item.evidence_type,
                    "artifact_type": item.artifact_type,
                    "source_identity": item.source_identity,
                    "coverage_start": item.coverage_start,
                    "coverage_end": item.coverage_end,
                    "row_count": item.row_count,
                    "schema": list(item.schema),
                    "provenance": cls._json_safe(item.provenance),
                    "neutral_semantics": item.neutral_semantics,
                }
                for item in evidence
            ],
            "evidence_continuity": {
                "comparison_statuses": ["SAME", "CHANGED", "UNVERIFIABLE"],
                "changed_is_not_scientific_failure": True,
                "comparison_fields": ["subject_id", "evidence_type", "artifact_type", "source_identity", "coverage_start", "coverage_end", "row_count", "schema", "provenance", "neutral_semantics"],
                "meaning": "If evidence is reacquired, deterministic code reports objective changes. The Research Director determines their scientific consequence.",
            },
            "hard_execution_failures": [
                "malformed AI decision representation",
                "nonexistent requested method",
                "missing required method parameter disclosed in method_contracts",
                "invalid parameter type/cardinality/value disclosed in method_contracts",
                "missing requested evidence identity",
                "missing requested prior Analysis result in the active runtime",
                "missing requested output_path in a prior Analysis result",
                "subject/evidence/result lineage mismatch",
                "required evidence payload unavailable for execution",
                "malformed finding envelope disclosed in finding_envelope",
            ],
        }

    def _request_decision(self, *, operation: str, mission: str, payload: Mapping[str, object]) -> ResearchDecision:
        system = (
            "You are the AI Research Director for Momentum Trading System v4. "
            "You are the scientific reasoning authority. Determine scientific questions, hypotheses, method choice, scientifically meaningful parameters, interpretation, significance, findings, and next research direction. "
            "The available Analysis methods are described neutrally in the supplied capability catalog; select from that catalog when requesting Analysis. "
            "You may explicitly chain a prior Analysis output into a later Analysis request using analysis_inputs; you decide which prior result and exact output path are scientifically appropriate. Deterministic code only resolves your exact reference and preserves its lineage. "
            "Every deterministic condition that can block your request or finding must be disclosed in objective_execution_requirements before it is enforced. Deterministic code validates only objective execution and representation contracts and may return exact defects for you to repair. It may not veto a scientific finding because the conclusion or metadata taxonomy was not anticipated. "
            "A changed evidence reacquisition is reported to you as evidence continuity metadata, not automatically treated as scientific failure. A missing calculation capability, data resource, or other research resource is also not scientific closure. Record such an unanswered question as LACK_RESOURCE in research_state, identify the resource needed, and continue to another scientifically useful answerable question whenever one remains. "
            "Resource gaps are operational research state, never scientific findings for Nexus. Nexus is durable research memory for subject metadata and significant findings, not a raw-data repository. Return exactly one JSON object matching the required decision schema and no prose."
        )
        user = {
            "operation": operation,
            "mission": mission,
            "required_decision_schema": {
                "continue_research": "boolean",
                "next_request": {
                    "request_id": "string",
                    "subject_id": "string",
                    "question": "string",
                    "method_id": "string from available_analysis_methods",
                    "evidence_ids": ["string"],
                    "analysis_inputs": [
                        {
                            "result_id": "exact prior analysis_result.result_id",
                            "output_path": ["string or integer path component"],
                            "input_name": "unique string name for this resolved execution payload",
                        }
                    ],
                    "parameters": {},
                    "research_phase": "EXPLORATION or VALIDATION",
                    "rationale": "string",
                },
                "promote_findings": [
                    {
                        "finding_id": "string",
                        "subject_id": "string",
                        "statement": "string",
                        "supporting_result_ids": ["string"],
                        "evidence_ids": ["string"],
                        "metadata": "open-ended object; arbitrary RD-authored scientific metadata allowed",
                    }
                ],
                "research_state": {
                    "questions_answered": "cumulative integer count maintained by RD",
                    "questions_unanswered_lack_resource": "cumulative integer count maintained by RD",
                    "lack_resource": [
                        {
                            "question": "unanswered scientific question",
                            "required_resources": ["resource, evidence, calculation, or capability needed"],
                            "reason": "brief explanation of why current resources cannot answer it",
                        }
                    ],
                    "other_state": "arbitrary additional AI-authored research state may be included",
                },
                "close_reason": "string or null",
            },
            "instructions": [
                "If continue_research is true, next_request must be fully authored by you.",
                "Choose the scientific method yourself from available_analysis_methods; capability metadata describes execution requirements but does not recommend a method.",
                "Review objective_execution_requirements before authoring a request or finding; these are the deterministic conditions either can be judged against.",
                "When a prior Analysis result contains a derived dataset needed by your next method, use analysis_inputs to identify the exact prior result_id and output_path. For example, a transform result whose derived rows are under observations can be referenced with output_path [\"observations\"], and you must then select columns that actually exist in those derived rows rather than silently reverting to raw evidence columns.",
                "Do not expect deterministic code to infer which prior result, output path, or derived field you intended; if you omit analysis_inputs, only evidence_ids are supplied as execution payloads.",
                "Derived Analysis outputs are campaign-local temporary data. If a process restart makes a referenced result unavailable, deterministic validation will report MISSING_ANALYSIS_RESULT and you decide whether regenerating that derived result is scientifically appropriate.",
                "If operation is RESUME_RESEARCH, inspect evidence_continuity and decide its scientific consequence yourself; CHANGED is not an automatic failure.",
                "If an objective contract defect is supplied, repair only by making your own scientific choice; do not expect the validator to invent a value or substitute a method.",
                "If a scientifically relevant question cannot be answered because a needed capability, dataset, field, coverage interval, or other resource is unavailable, append it to research_state.lack_resource with the required resources and reason, then move to another answerable question rather than ending the campaign solely for that gap.",
                "Maintain cumulative research_state.questions_answered and research_state.questions_unanswered_lack_resource so the final decision reports how many questions were answered and how many remain unanswered for lack of resources.",
                "When the campaign eventually closes, preserve the full cumulative research_state.lack_resource list as the end-of-run resource request report.",
                "Do not promote missing tools, missing data, unsupported calculations, or other resource/capability limitations as scientific findings; they belong in research_state only.",
                "Set continue_research false for lack of resources only if, in your scientific judgment, no other meaningful answerable research question remains or the campaign is otherwise complete.",
                "Promote findings only when you judge them scientifically significant enough for durable research memory.",
                "The finding envelope is closed and minimal; the metadata namespace is scientifically open-ended and does not require an approved vocabulary.",
                "Do not place raw/reproducible datasets in findings or research_state.",
            ],
            "context": payload,
        }
        body = json.dumps({"model": self._model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user, sort_keys=True, default=str)}], "temperature": 0.2}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(f"{self._base_url}/v1/chat/completions", data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                document = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise ResearchDirectorTransportError(f"AI Research Director transport failed: {type(exc).__name__}: {exc}") from exc

        try:
            message = document["choices"][0]["message"]
            content = message.get("content")
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ResearchDirectorTransportError("OpenAI-compatible response is missing choices[0].message") from exc
        if not isinstance(content, str) or not content.strip():
            reasoning_content = message.get("reasoning_content") if isinstance(message, Mapping) else None
            if isinstance(reasoning_content, str) and reasoning_content.strip():
                content = reasoning_content
            else:
                raise ResearchDirectorTransportError("AI Research Director returned no textual decision")
        return ResearchDecisionCodec.decode(content)

    @staticmethod
    def _json_safe(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Mapping):
            return {str(k): OpenAICompatibleResearchDirector._json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [OpenAICompatibleResearchDirector._json_safe(v) for v in value]
        if hasattr(value, "__dataclass_fields__"):
            return OpenAICompatibleResearchDirector._json_safe(asdict(value))
        return value
