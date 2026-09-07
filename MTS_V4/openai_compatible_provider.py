from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from enum import Enum
from typing import Any, Mapping, Sequence

from .contracts import (
    AnalysisRequest,
    AnalysisResult,
    ContractDefect,
    EvidenceDescriptor,
    ResearchDecision,
    SubjectMetadata,
)
from .rd_codec import ResearchDecisionCodec, ResearchDecisionDecodeError


class ResearchDirectorTransportError(RuntimeError):
    pass


class OpenAICompatibleResearchDirector:
    """OpenAI-compatible transport for the v4 AI Research Director."""

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

    def begin_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        return self._request_decision(
            operation="BEGIN_RESEARCH",
            mission=mission,
            payload=self._common_payload(
                subject=subject,
                evidence=evidence,
                available_methods=available_methods,
                nexus_context=nexus_context,
            ),
        )

    def resume_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: ResearchDecision,
        evidence_continuity: Mapping[str, object],
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        payload = self._common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload.update(
            {
                "prior_decision": self._json_safe(asdict(prior_decision)),
                "evidence_continuity": self._json_safe(evidence_continuity),
            }
        )
        return self._request_decision(
            operation="RESUME_RESEARCH", mission=mission, payload=payload
        )

    def repair_request(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: ResearchDecision,
        defects: Sequence[ContractDefect],
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        payload = self._common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload.update(
            {
                "prior_decision": self._json_safe(asdict(prior_decision)),
                "objective_contract_defects": [asdict(item) for item in defects],
            }
        )
        return self._request_decision(
            operation="REPAIR_OBJECTIVE_CONTRACT", mission=mission, payload=payload
        )

    def interpret_result(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
        result: AnalysisResult,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        payload = self._common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload.update(
            {
                "analysis_request": self._json_safe(asdict(request)),
                "analysis_result": self._analysis_result_payload(result),
            }
        )
        return self._request_decision(
            operation="INTERPRET_ANALYSIS_RESULT", mission=mission, payload=payload
        )

    @classmethod
    def _common_payload(
        cls,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> dict[str, object]:
        """Build one authoritative copy of each RD-visible catalog.

        Deterministic execution requirements refer to these adjacent objects by
        path rather than serializing the method and evidence catalogs a second
        time. No scientific information is removed or summarized.
        """
        return {
            "subject": asdict(subject),
            "evidence": [asdict(item) for item in evidence],
            "available_analysis_methods": cls._json_safe(available_methods),
            "objective_execution_requirements": cls._execution_requirements(
                evidence=evidence,
                available_methods=available_methods,
            ),
            "nexus_context": cls._json_safe(nexus_context),
        }

    @classmethod
    def _execution_requirements(
        cls,
        *,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, object]:
        """Publish every deterministic condition RD can be held to.

        ``evidence`` and ``available_methods`` are accepted so callers retain one
        stable interface. Their complete contents are already present once in the
        same context object and are referenced here instead of duplicated.
        """
        return {
            "visibility_rule": (
                "Any deterministic requirement that can reject or block an AI Research Director "
                "request or finding must be disclosed to the Research Director before the request "
                "or finding is judged against it."
            ),
            "catalog_references": {
                "method_contracts": "context.available_analysis_methods",
                "available_evidence": "context.evidence",
                "meaning": (
                    "These are exact references to the complete adjacent catalogs in this same "
                    "request. They are not summaries and no contract/evidence metadata is omitted."
                ),
                "method_count": len(available_methods),
                "evidence_count": len(evidence),
            },
            "analysis_request": {
                "method_id": "must identify an available_analysis_methods entry exactly",
                "subject_id": "must equal the active subject_id",
                "evidence_ids": (
                    "must always be present as a list; identify supplied raw evidence exactly, "
                    "or use [] when execution uses no raw evidence"
                ),
                "analysis_inputs": (
                    "must always be present as a list; use [] when no prior Analysis output is used. "
                    "Each entry must supply result_id, exact output_path, and input_name. output_path "
                    "is always relative to analysis_result.outputs; do not include an initial 'outputs' "
                    "component. Reusable row datasets are advertised in derived_dataset_catalog with "
                    "their exact output_path and schema. Deterministic code resolves only the exact "
                    "RD-authored reference and may not choose or substitute a prior result or output. "
                    "Prior derived outputs are temporary and are not persisted through process restart; "
                    "an unavailable result is returned as an objective defect so RD may decide whether "
                    "to regenerate it."
                ),
                "method_contracts_reference": "context.available_analysis_methods",
                "no_hidden_defaults": (
                    "Scientifically meaningful missing parameters are not inferred, defaulted, or "
                    "substituted by deterministic code."
                ),
            },
            "finding_envelope": {
                "closed_required_fields": [
                    "finding_id",
                    "subject_id",
                    "statement",
                    "supporting_result_ids",
                    "evidence_ids",
                ],
                "metadata": (
                    "open-ended object authored by RD; arbitrary scientific labels, nested structures, "
                    "classifications, applicability, limitations, relationships, confidence judgments, "
                    "or previously unanticipated concepts are permitted"
                ),
                "reference_validation": (
                    "evidence_ids and supporting_result_ids must resolve to durable identity/lineage "
                    "metadata for the same subject; raw historical result payloads are not required"
                ),
                "scientific_taxonomy_is_open": True,
                "deterministic_scientific_veto": False,
                "meaning": (
                    "Deterministic code may validate only representation, identity, and lineage. It may "
                    "not reject a finding because its scientific conclusion, category, label, or metadata "
                    "was not anticipated by code."
                ),
            },
            "available_evidence_reference": "context.evidence",
            "evidence_continuity": {
                "comparison_statuses": ["SAME", "CHANGED", "UNVERIFIABLE"],
                "changed_is_not_scientific_failure": True,
                "content_identity_compared_separately": True,
                "acquisition_timestamps_are_not_content_identity": True,
                "meaning": (
                    "If evidence is reacquired, deterministic code reports objective content/source "
                    "changes separately from operational acquisition time. The Research Director "
                    "determines their scientific consequence."
                ),
            },
            "future_information_lineage": {
                "propagated_through_analysis_chaining": True,
                "blanket_rejection": False,
                "meaning": (
                    "Deterministic code records whether a result directly or transitively contains "
                    "future information. It does not decide whether that information is scientifically "
                    "appropriate; RD owns exploratory use and later validation design."
                ),
            },
            "hard_execution_failures": [
                "malformed AI decision representation",
                "nonexistent requested method",
                "missing required method parameter disclosed in available_analysis_methods",
                "invalid parameter type/cardinality/value disclosed in available_analysis_methods",
                "missing requested evidence identity",
                "missing requested prior Analysis result in the active runtime",
                "missing requested output_path in a prior Analysis result",
                "subject/evidence/result lineage mismatch",
                "required evidence payload unavailable for execution",
                "malformed finding envelope disclosed in finding_envelope",
            ],
            "analysis_execution_error_policy": (
                "If the exact requested Analysis method encounters an objective execution error, the "
                "error is returned as an Analysis result with interpretation_boundary "
                "OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP. Deterministic code does not choose a "
                "replacement method, input, preprocessing step, or scientific response."
            ),
            "decision_representation_repair_policy": (
                "If your returned JSON cannot be decoded because a required representation field is "
                "missing or malformed, the transport may return the exact decode defect to you once and "
                "ask you to author a corrected complete decision. Deterministic code does not fill the "
                "missing field or alter your scientific choices."
            ),
        }

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are the AI Research Director for Momentum Trading System v4. "
            "You are the scientific reasoning authority. Determine scientific questions, hypotheses, "
            "method choice, scientifically meaningful parameters, interpretation, significance, findings, "
            "and next research direction. The available Analysis methods are described neutrally in the "
            "supplied capability catalog; select from that catalog when requesting Analysis. You may "
            "explicitly chain a prior Analysis output into a later Analysis request using analysis_inputs; "
            "you decide which prior result and exact output path are scientifically appropriate. "
            "Deterministic code only resolves your exact reference and preserves its lineage. Reusable "
            "derived row datasets are temporary campaign-local Analysis outputs advertised in "
            "derived_dataset_catalog; their row payloads are withheld from model transport but remain "
            "mechanically available to later Analysis execution through the catalog's exact output_path. "
            "Every deterministic condition that can block your request or finding must be disclosed in "
            "objective_execution_requirements before it is enforced. Deterministic code validates only "
            "objective execution, identity, lineage, and representation contracts and may return exact "
            "defects for you to repair. It may not veto a scientific finding because the conclusion or "
            "metadata taxonomy was not anticipated. A changed evidence reacquisition is reported to you "
            "as evidence continuity metadata, not automatically treated as scientific failure. Future-"
            "information lineage is also reported mechanically and is not a blanket rejection rule. A "
            "missing calculation capability, data resource, or other research resource is not scientific "
            "closure. Record such an unanswered question as LACK_RESOURCE in research_state, identify the "
            "resource needed, and continue to another scientifically useful answerable question whenever "
            "one remains. Resource gaps are operational research state, never scientific findings for "
            "Nexus. Nexus is durable research memory for subject metadata, identity/lineage metadata, and "
            "significant findings, not a raw-data repository. Return exactly one JSON object matching the "
            "required decision schema and no prose."
        )

    @classmethod
    def _decision_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
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
                    "evidence_ids": "REQUIRED list of raw evidence IDs; use [] when none",
                    "analysis_inputs": [
                        {
                            "result_id": "exact prior analysis_result.result_id",
                            "output_path": [
                                "path components relative to analysis_result.outputs; never prefix with outputs"
                            ],
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
                            "required_resources": [
                                "resource, evidence, calculation, or capability needed"
                            ],
                            "reason": "brief explanation of why current resources cannot answer it",
                        }
                    ],
                    "other_state": "arbitrary additional AI-authored research state may be included",
                },
                "close_reason": "string or null",
            },
            "instructions": [
                "If continue_research is true, next_request must be fully authored by you.",
                "Every next_request must explicitly contain both evidence_ids and analysis_inputs. Use [] for either list when you intentionally use none; never omit either field.",
                "Choose the scientific method yourself from available_analysis_methods; capability metadata describes execution requirements but does not recommend a method.",
                "Review objective_execution_requirements before authoring a request or finding; these are the deterministic conditions either can be judged against. Catalog references point to complete adjacent objects in the same context and are not summaries.",
                "When analysis_result.outputs.derived_dataset_catalog advertises a dataset needed by your next method, use its exact output_path in analysis_inputs. output_path is relative to analysis_result.outputs, so never prefix it with 'outputs'.",
                "Syntactic chaining example only: if the current result_id is analysis-result:1 and its catalog advertises output_path [\"derived_datasets\", \"forward_path_observations\"], a request using only that dataset must contain evidence_ids: [] and analysis_inputs: [{\"result_id\":\"analysis-result:1\",\"output_path\":[\"derived_datasets\",\"forward_path_observations\"],\"input_name\":\"forward_path_observations\"}]. This illustrates representation only and does not recommend any scientific method, horizon, field, or question.",
                "Select only columns actually listed in the chosen derived dataset schema. Do not silently revert to raw evidence columns when your question concerns a derived quantity.",
                "Do not expect deterministic code to infer which prior result, derived dataset, output path, or derived field you intended; if analysis_inputs is [], only evidence_ids are supplied as execution payloads.",
                "For analysis.toolkit.scientific_function, each item in args is one positional argument to the selected SciPy function. A {\"column\":\"field\"} item binds one complete column as one positional argument. Do not list multiple columns as separate args unless the selected SciPy signature actually accepts those arrays as separate positional arguments.",
                "Derived Analysis outputs are campaign-local temporary data. If a process restart makes a referenced result unavailable, deterministic validation will report MISSING_ANALYSIS_RESULT and you decide whether regenerating that derived result is scientifically appropriate.",
                "An Analysis result with interpretation_boundary OBJECTIVE_EXECUTION_ERROR_RD_DECIDES_NEXT_STEP reports an objective failure of the exact method you requested; decide the scientific next step yourself rather than assuming the runtime substituted another method.",
                "If operation is RESUME_RESEARCH, inspect evidence_continuity and decide its scientific consequence yourself; CHANGED is not an automatic failure.",
                "If future_information lineage is present, treat it as provenance. Exploratory lookahead remains allowed; determine its scientific consequence yourself and design later validation appropriately.",
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
        return [
            {"role": "system", "content": cls._system_prompt()},
            {"role": "user", "content": json.dumps(user, sort_keys=True, default=str)},
        ]

    def _request_decision(
        self,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> ResearchDecision:
        messages = self._decision_messages(
            operation=operation,
            mission=mission,
            payload=payload,
        )
        content = self._chat_completion(messages)
        try:
            return ResearchDecisionCodec.decode(content)
        except ResearchDecisionDecodeError as exc:
            repair_instruction = {
                "operation": "REPAIR_DECISION_REPRESENTATION",
                "decode_defect": str(exc),
                "instruction": (
                    "Return one complete corrected decision JSON object. Preserve or revise your own "
                    "scientific choices as you judge appropriate, but satisfy the required decision "
                    "representation. Deterministic code will not fill any missing scientific field for you. "
                    "If continue_research is true, next_request must explicitly include evidence_ids and "
                    "analysis_inputs; use [] when you intentionally use none."
                ),
            }
            repaired_content = self._chat_completion(
                messages
                + [
                    {"role": "assistant", "content": content},
                    {"role": "user", "content": json.dumps(repair_instruction, sort_keys=True)},
                ]
            )
            return ResearchDecisionCodec.decode(repaired_content)

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": list(messages),
                "temperature": 0.2,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(
            f"{self._base_url}/v1/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                document = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                response_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                response_body = ""
            detail = f"; response_body={response_body}" if response_body else ""
            raise ResearchDirectorTransportError(
                f"AI Research Director transport failed: HTTPError: {exc}{detail}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ResearchDirectorTransportError(
                f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
            ) from exc

        try:
            message = document["choices"][0]["message"]
            content = message.get("content")
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ResearchDirectorTransportError(
                "OpenAI-compatible response is missing choices[0].message"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            reasoning_content = message.get("reasoning_content") if isinstance(message, Mapping) else None
            if isinstance(reasoning_content, str) and reasoning_content.strip():
                content = reasoning_content
            else:
                raise ResearchDirectorTransportError(
                    "AI Research Director returned no textual decision"
                )
        return content

    @classmethod
    def _analysis_result_payload(cls, result: AnalysisResult) -> Mapping[str, object]:
        raw = asdict(result)
        outputs = dict(raw.get("outputs", {}))
        derived = outputs.pop("derived_datasets", None)
        if isinstance(derived, Mapping):
            catalog = outputs.get("derived_dataset_catalog")
            if not isinstance(catalog, Mapping):
                catalog = {
                    str(name): {
                        "row_count": len(rows) if isinstance(rows, (list, tuple)) else None,
                        "output_path": ["derived_datasets", str(name)],
                        "temporary": True,
                    }
                    for name, rows in derived.items()
                }
                outputs["derived_dataset_catalog"] = catalog
            outputs["derived_dataset_transport"] = (
                "Row payload withheld from RD transport; available to later Analysis execution only "
                "through explicit analysis_inputs using the catalog's output_path."
            )
        raw["outputs"] = outputs
        return cls._json_safe(raw)

    @staticmethod
    def _json_safe(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Mapping):
            return {
                str(k): OpenAICompatibleResearchDirector._json_safe(v)
                for k, v in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [OpenAICompatibleResearchDirector._json_safe(v) for v in value]
        if hasattr(value, "__dataclass_fields__"):
            return OpenAICompatibleResearchDirector._json_safe(asdict(value))
        return value
