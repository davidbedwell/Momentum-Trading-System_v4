from __future__ import annotations

from dataclasses import asdict, replace
import json
from typing import Mapping, Sequence

from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, ResearchDecision, SubjectMetadata
from .openai_compatible_provider import OpenAICompatibleResearchDirector
from .rd_codec import ResearchDecisionCodec
from .research_package_store import JsonResearchPackageStore


class ResearchPackageAwareResearchDirector(OpenAICompatibleResearchDirector):
    """Production RD transport with explicit AI-authored research-package lineage.

    The additional contract gives RD a durable place to identify the coherent
    research package, question ancestry, and interpretation that it owns. The
    transport validates representation only; it never chooses those scientific
    relationships for RD.
    """

    _MAX_RP_REPRESENTATION_REPAIRS = 3

    def __init__(
        self,
        *,
        research_package_store: JsonResearchPackageStore,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self._research_package_store = research_package_store

    @classmethod
    def _decision_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
        messages = super()._decision_messages(
            operation=operation,
            mission=mission,
            payload=payload,
        )
        system = messages[0]["content"] + (
            " Every decision must identify the durable research package to which the current "
            "interpretation/findings belong with rp_id. Every next_request must also include rp_id, "
            "question_id, parent_question_id, and parent_rp_id. You decide whether a follow-up remains "
            "in the existing RP or starts a new child RP; deterministic code only preserves the lineage "
            "you author. A later RP never overwrites an earlier RP. A question may not name itself as "
            "its parent, and an RP may not name itself as its parent. Every new Analysis execution "
            "attempt must use a request_id that has not already been durably used. When interpreting "
            "an Analysis result, provide a substantive analysis_interpretation even when no finding is promoted."
        )
        user = json.loads(messages[1]["content"])
        schema = user["required_decision_schema"]
        schema["rp_id"] = (
            "nonblank string: RP to which this decision's interpretation/findings belong"
        )
        schema["analysis_interpretation"] = (
            "string or null; substantive string required when operation is INTERPRET_ANALYSIS_RESULT"
        )
        next_request = schema["next_request"]
        next_request["rp_id"] = (
            "nonblank string: RP containing the requested question; may differ from decision rp_id only when RD intentionally branches to another RP"
        )
        next_request["question_id"] = "nonblank stable question identifier within this RP"
        next_request["parent_question_id"] = (
            "string or null; null for root question, otherwise exact different prior question_id in same RP"
        )
        next_request["parent_rp_id"] = (
            "string or null; when used, exact different prior rp_id from which a distinct child RP emerged"
        )
        user["instructions"].extend(
            [
                "Use context.research_packages as durable scientific memory for prior/open RP identity, lineage, findings, unresolved issues, and closure assessments.",
                "Keep follow-up questions under the same rp_id when they continue the same coherent scientific line; assign parent_question_id to the different prior question that caused the follow-up.",
                "Create a new next_request.rp_id only when you judge a materially distinct research proposition has emerged; when it is a child of prior work, identify the different parent_rp_id yourself.",
                "Never set parent_question_id equal to question_id and never set parent_rp_id equal to rp_id; self-parent lineage is mechanically invalid.",
                "Every new Analysis execution attempt requires a new request_id. If you revise parameters, method, inputs, or any other execution contract after interpreting a prior result, assign a new request_id even when the scientific question_id remains the same.",
                "decision.rp_id identifies the RP owning the current interpretation/findings; next_request.rp_id identifies the RP owning the next question. They normally match, but may differ when you intentionally branch to a new RP.",
                "Never reuse a prior rp_id for unrelated work and never treat a new RP as replacement for an earlier RP.",
                "On INTERPRET_ANALYSIS_RESULT, decision.rp_id must be the same RP as the Analysis request being interpreted.",
                "On INTERPRET_ANALYSIS_RESULT, state what you learned in analysis_interpretation whether or not it is significant enough to promote as a finding.",
                "On final scientific closure, rp_id identifies the RP being closed and close_reason states your scientific reason.",
            ]
        )
        return [
            {"role": "system", "content": system},
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
        enriched_payload = dict(payload)
        subject = enriched_payload.get("subject")
        subject_id = subject.get("subject_id") if isinstance(subject, Mapping) else None
        if isinstance(subject_id, str) and subject_id:
            enriched_payload["research_packages"] = self._research_package_store.context_for_subject(
                subject_id
            )

        decision = super()._request_decision(
            operation=operation,
            mission=mission,
            payload=enriched_payload,
        )
        defect = self._decision_representation_defect(operation, decision, enriched_payload)
        if defect is None:
            return decision

        messages = self._decision_messages(
            operation=operation,
            mission=mission,
            payload=enriched_payload,
        )
        for _ in range(self._MAX_RP_REPRESENTATION_REPAIRS):
            repaired = self._chat_completion(
                messages
                + [
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            asdict(decision),
                            sort_keys=True,
                            default=str,
                            separators=(",", ":"),
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "operation": "REPAIR_RESEARCH_PACKAGE_REPRESENTATION",
                                "decode_defect": defect,
                                "instruction": (
                                    "Return one complete corrected decision JSON object. Correct the exact "
                                    "objective identity/lineage defect identified above. You retain full scientific "
                                    "authority over RP identity, question lineage, interpretation, and next "
                                    "direction. Deterministic code will not invent, replace, or select any of "
                                    "those scientific values; it only validates their explicit representation."
                                ),
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    },
                ]
            )
            decision = ResearchDecisionCodec.decode(repaired)
            defect = self._decision_representation_defect(operation, decision, enriched_payload)
            if defect is None:
                return decision

        raise ValueError(
            "research package representation repair budget exhausted: " + defect
        )

    def _decision_representation_defect(
        self,
        operation: str,
        decision: ResearchDecision,
        payload: Mapping[str, object],
    ) -> str | None:
        defect = self._rp_representation_defect(operation, decision, payload)
        if defect is not None:
            return defect
        if not decision.continue_research or decision.next_request is None:
            return None
        request_id = decision.next_request.request_id
        for rp_id in self._research_package_store.list_ids():
            package = self._research_package_store.load(rp_id)
            if package is None:
                continue
            if any(item.request_id == request_id for item in package.analyses):
                return (
                    "next_request.request_id has already been durably used; every new Analysis "
                    f"execution attempt requires a new request_id: {request_id}"
                )
        return None

    @staticmethod
    def _rp_representation_defect(
        operation: str,
        decision: ResearchDecision,
        payload: Mapping[str, object],
    ) -> str | None:
        if not decision.rp_id:
            return "decision requires nonblank rp_id"
        if decision.continue_research:
            request = decision.next_request
            if request is None:
                return "continuing decision requires next_request"
            if not request.rp_id:
                return "next_request requires nonblank rp_id"
            if not request.question_id:
                return "next_request requires nonblank question_id"
            if (
                request.parent_question_id is not None
                and request.parent_question_id == request.question_id
            ):
                return "parent_question_id may not equal question_id"
            if request.parent_rp_id is not None and request.parent_rp_id == request.rp_id:
                return "parent_rp_id may not equal rp_id"
            if operation == "BEGIN_RESEARCH" and request.rp_id != decision.rp_id:
                return "BEGIN_RESEARCH decision.rp_id must equal next_request.rp_id"
        if operation == "INTERPRET_ANALYSIS_RESULT":
            analysis_request = payload.get("analysis_request")
            interpreted_rp_id = (
                analysis_request.get("rp_id")
                if isinstance(analysis_request, Mapping)
                else None
            )
            if interpreted_rp_id and decision.rp_id != interpreted_rp_id:
                return (
                    "INTERPRET_ANALYSIS_RESULT decision.rp_id must equal the interpreted "
                    "Analysis request rp_id"
                )
            if not decision.analysis_interpretation or not decision.analysis_interpretation.strip():
                return "INTERPRET_ANALYSIS_RESULT requires substantive analysis_interpretation"
        return None

    def interpret_result(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
        result: AnalysisResult,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, object]],
        nexus_context: Mapping[str, object],
    ) -> ResearchDecision:
        decision = super().interpret_result(
            mission=mission,
            subject=subject,
            request=request,
            result=result,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        status = result.execution_metadata.get("execution_status")
        return replace(
            decision,
            interpreted_request_id=request.request_id,
            interpreted_result_id=result.result_id,
            interpreted_execution_status=(str(status) if status is not None else None),
        )
