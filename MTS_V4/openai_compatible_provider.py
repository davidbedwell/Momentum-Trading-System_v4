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
    """OpenAI-compatible transport for the v4 AI Research Director.

    Transport is deliberately bounded around current scientific context. Durable
    Nexus audit history may be much larger than the scientific memory that RD
    previously promoted as significant; the former is not blindly serialized on
    every turn. No deterministic scientific ranking or selection is performed.
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
        """Build one copy of current RD-visible evidence/method context.

        The orchestrator supplies a full durable Nexus view for mechanical use.
        Transport removes objects already supplied adjacent to it and historical
        Analysis audit records that contain no scientific result payload. Exact
        lineage for Analysis results cited by RD-promoted significant findings is
        preserved. This uses RD's own promotion decisions, not deterministic
        scientific relevance scoring.
        """
        return {
            "subject": asdict(subject),
            "evidence": [asdict(item) for item in evidence],
            "available_analysis_methods": cls._json_safe(available_methods),
            "objective_execution_requirements": cls._execution_requirements(
                evidence=evidence,
                available_methods=available_methods,
            ),
            "nexus_context": cls._compact_nexus_context(nexus_context),
        }

    @classmethod
    def _compact_nexus_context(
        cls, nexus_context: Mapping[str, object]
    ) -> Mapping[str, object]:
        raw = dict(nexus_context)
        findings = tuple(raw.get("significant_findings", ()) or ())
        historical = tuple(raw.get("historical_analysis_result_metadata", ()) or ())
        evidence_metadata = tuple(raw.get("evidence_metadata", ()) or ())

        cited_result_ids: set[str] = set()
        for finding in findings:
            if isinstance(finding, Mapping):
                values = finding.get("supporting_result_ids", ())
            else:
                values = getattr(finding, "supporting_result_ids", ())
            if isinstance(values, (list, tuple, set)):
                cited_result_ids.update(str(value) for value in values)

        finding_lineage = []
        for item in historical:
            result_id = (
                item.get("result_id")
                if isinstance(item, Mapping)
                else getattr(item, "result_id", None)
            )
            if result_id is None or str(result_id) not in cited_result_ids:
                continue
            finding_lineage.append(cls._json_safe(item))

        compact = {
            key: value
            for key, value in raw.items()
            if key
            not in {
                "subject",
                "evidence_metadata",
                "historical_analysis_result_metadata",
            }
        }
        compact["significant_findings"] = cls._json_safe(findings)
        compact["historical_finding_support_lineage"] = finding_lineage
        compact["durable_inventory"] = {
            "evidence_metadata_count": len(evidence_metadata),
            "historical_analysis_result_metadata_count": len(historical),
            "significant_finding_count": len(findings),
            "historical_result_metadata_embedded_count": len(finding_lineage),
        }
        compact["transport_policy"] = {
            "subject_and_evidence_are_supplied_once_adjacent_to_nexus_context": True,
            "unpromoted_historical_analysis_results_are_audit_lineage_not_scientific_memory": True,
            "significant_findings_are_rd_selected_not_deterministically_filtered": True,
            "lineage_for_results_supporting_significant_findings_is_embedded": True,
            "deterministic_scientific_ranking_or_selection": False,
        }
        return cls._json_safe(compact)

    @classmethod
    def _execution_requirements(
        cls,
        *,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, object]:
        """Compact disclosure of every deterministic rejection class."""
        return {
            "visibility_rule": (
                "Any deterministic requirement that can reject or block an RD request or finding "
                "must be disclosed before it is enforced."
            ),
            "catalog_references": {
                "method_contracts": "context.available_analysis_methods",
                "available_evidence": "context.evidence",
                "method_count": len(available_methods),
                "evidence_count": len(evidence),
            },
            "analysis_request": {
                "method_id": "exact available method_id",
                "subject_id": "active subject_id",
                "evidence_ids": "required list; [] allowed",
                "analysis_inputs": (
                    "required list; [] allowed; each item requires result_id, output_path relative to "
                    "analysis_result.outputs, and unique input_name"
                ),
                "method_contracts_reference": "context.available_analysis_methods",
                "no_hidden_defaults": True,
            },
            "finding_envelope": {
                "closed_required_fields": [
                    "finding_id",
                    "subject_id",
                    "statement",
                    "supporting_result_ids",
                    "evidence_ids",
                ],
                "metadata": "open-ended RD-authored scientific object",
                "reference_validation": "same-subject evidence/result identity and lineage only",
                "scientific_taxonomy_is_open": True,
                "deterministic_scientific_veto": False,
            },
            "available_evidence_reference": "context.evidence",
            "evidence_continuity": {
                "comparison_statuses": ["SAME", "CHANGED", "UNVERIFIABLE"],
                "changed_is_not_scientific_failure": True,
                "content_identity_compared_separately": True,
                "acquisition_timestamps_are_not_content_identity": True,
            },
            "future_information_lineage": {
                "propagated_through_analysis_chaining": True,
                "blanket_rejection": False,
                "rd_decides_scientific_use": True,
            },
            "hard_execution_failures": [
                "malformed_decision_representation",
                "nonexistent_method",
                "missing_required_method_parameter",
                "invalid_parameter_contract",
                "missing_evidence_identity",
                "missing_active_runtime_analysis_result",
                "missing_prior_result_output_path",
                "subject_evidence_result_lineage_mismatch",
                "required_evidence_payload_unavailable",
                "malformed_finding_envelope",
            ],
            "analysis_execution_error_policy": (
                "Return the exact execution error to RD; do not choose replacement method/input/parameter."
            ),
            "decision_representation_repair_policy": (
                "Return exact decode defect once; deterministic code does not fill scientific fields."
            ),
        }

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are the AI Research Director for Momentum Trading System v4 and the scientific "
            "reasoning authority. You own questions, hypotheses, method and scientific-parameter choice, "
            "interpretation, significance, findings, uncertainty, and next direction. Deterministic code "
            "may enforce only disclosed execution, representation, identity, lineage, temporal-phase, and "
            "resource-safety contracts; it may not substitute scientific judgment. Derived row datasets "
            "remain campaign-local and are chainable only through exact analysis_inputs paths. Changed "
            "evidence and future-information flags are provenance for you to interpret, not automatic "
            "scientific failures. Missing resources belong in research_state.lack_resource, not findings. "
            "Nexus stores durable significant scientific memory and lineage, not raw/reproducible data. "
            "Return exactly one decision JSON object and no prose."
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
                    "method_id": "available method_id",
                    "evidence_ids": "required list; [] allowed",
                    "analysis_inputs": [
                        {
                            "result_id": "exact prior result_id",
                            "output_path": ["components relative to analysis_result.outputs"],
                            "input_name": "unique string",
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
                        "metadata": "open-ended scientific object",
                    }
                ],
                "research_state": {
                    "questions_answered": "cumulative integer",
                    "questions_unanswered_lack_resource": "cumulative integer",
                    "lack_resource": [
                        {
                            "question": "string",
                            "required_resources": ["string"],
                            "reason": "string",
                        }
                    ],
                    "other_state": "arbitrary RD-authored state allowed",
                },
                "close_reason": "string or null",
            },
            "instructions": [
                "If continue_research=true, fully author next_request with evidence_ids and analysis_inputs; use [] intentionally, never omit either.",
                "Select methods and scientifically meaningful parameters yourself from available_analysis_methods; deterministic code supplies no scientific defaults.",
                "Use exact derived_dataset_catalog output_path values for chaining; output_path is relative to analysis_result.outputs and never begins with outputs.",
                "Use only fields actually present in the selected evidence or derived schema.",
                "For analysis.toolkit.scientific_function, each args item is one positional argument; {column:field} binds one whole column.",
                "Treat objective execution defects, evidence continuity, and future-information metadata as facts for your scientific judgment, not deterministic scientific conclusions.",
                "Record scientifically relevant unavailable resources in cumulative research_state.lack_resource and continue with another useful answerable question when one remains.",
                "Promote only findings you judge significant; finding metadata vocabulary is open-ended; never place raw/reproducible datasets in findings or research_state.",
                "Campaign-local derived outputs disappear across process restart unless regenerated by an RD-authored Analysis request.",
            ],
            "context": payload,
        }
        return [
            {"role": "system", "content": cls._system_prompt()},
            {
                "role": "user",
                "content": json.dumps(
                    user,
                    sort_keys=True,
                    default=str,
                    separators=(",", ":"),
                ),
            },
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
                    "representation. Deterministic code will not fill missing scientific fields. If "
                    "continue_research is true, next_request must contain evidence_ids and analysis_inputs."
                ),
            }
            repaired_content = self._chat_completion(
                messages
                + [
                    {"role": "assistant", "content": content},
                    {
                        "role": "user",
                        "content": json.dumps(
                            repair_instruction,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    },
                ]
            )
            return ResearchDecisionCodec.decode(repaired_content)

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": list(messages),
                "temperature": 0.2,
            },
            separators=(",", ":"),
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
        """Return the RD-visible result while withholding campaign-local row payloads."""
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

            withheld_aliases: dict[str, Mapping[str, object]] = {}
            protected_keys = {
                "derived_dataset_catalog",
                "derived_dataset_transport",
                "withheld_row_output_aliases",
            }
            for dataset_name, rows in derived.items():
                if not isinstance(rows, (list, tuple)):
                    continue
                dataset_metadata = (
                    catalog.get(str(dataset_name), {})
                    if isinstance(catalog, Mapping)
                    else {}
                )
                output_path = (
                    dataset_metadata.get("output_path")
                    if isinstance(dataset_metadata, Mapping)
                    else None
                )
                if not isinstance(output_path, (list, tuple)):
                    output_path = ["derived_datasets", str(dataset_name)]
                for key, value in tuple(outputs.items()):
                    if key in protected_keys:
                        continue
                    if isinstance(value, (list, tuple)) and value == rows:
                        outputs.pop(key, None)
                        withheld_aliases[str(key)] = {
                            "dataset_name": str(dataset_name),
                            "output_path": list(output_path),
                            "row_count": len(rows),
                        }

            outputs["derived_dataset_transport"] = (
                "Row payload withheld from RD transport; available to later Analysis execution only "
                "through explicit analysis_inputs using the catalog's output_path."
            )
            if withheld_aliases:
                outputs["withheld_row_output_aliases"] = {
                    "meaning": (
                        "These output keys were exact aliases of campaign-local derived row datasets; "
                        "use the listed output_path through analysis_inputs if scientifically needed."
                    ),
                    "aliases": withheld_aliases,
                }
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
