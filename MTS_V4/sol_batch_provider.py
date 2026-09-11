from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any, Mapping, Sequence

from .batch_contracts import BatchExecutionReport, BatchResearchDecision
from .batch_rd_codec import BatchResearchDecisionCodec, BatchResearchDecisionDecodeError
from .contracts import EvidenceDescriptor, SubjectMetadata
from .sol_primary_provider import SolPrimaryResearchDirector


class SolBatchResearchDirector(SolPrimaryResearchDirector):
    """Program-level Sol RD that authors multiple RPs and Analysis Specifications per turn."""

    _MAX_BATCH_REPRESENTATION_REPAIRS = 2

    def begin_batch_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> BatchResearchDecision:
        payload = self._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        return self._request_batch_decision(
            operation="BEGIN_BATCH_RESEARCH",
            mission=mission,
            payload=payload,
        )

    def interpret_batch_results(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: BatchResearchDecision,
        report: BatchExecutionReport,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> BatchResearchDecision:
        payload = self._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload["prior_batch_decision"] = self._json_safe(asdict(prior_decision))
        payload["batch_execution_report"] = self._report_payload(report)
        return self._request_batch_decision(
            operation="INTERPRET_BATCH_RESULTS",
            mission=mission,
            payload=payload,
        )

    def repair_batch_plan(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        prior_decision: BatchResearchDecision,
        defects: Sequence[Mapping[str, object]],
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> BatchResearchDecision:
        payload = self._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload["prior_batch_decision"] = self._json_safe(asdict(prior_decision))
        payload["objective_batch_defects"] = self._json_safe(defects)
        return self._request_batch_decision(
            operation="REPAIR_BATCH_PLAN",
            mission=mission,
            payload=payload,
        )

    def _batch_common_payload(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> dict[str, object]:
        payload = self._common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
        )
        payload["research_packages"] = self._research_package_store.context_for_subject(
            subject.subject_id
        )
        if self._required_research_phase is not None:
            payload["subject_phase_contract"] = {
                "subject_id": self._required_subject_id,
                "required_research_phase": self._required_research_phase.value,
                "authority": (
                    "Accepted subject program phase. Every Analysis Specification in this batch for the "
                    "active subject must use this phase; deterministic code will not choose scientific work."
                ),
            }
        return payload

    @classmethod
    def _batch_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
        system = (
            "You are the AI Research Director for Momentum Trading System v4 and the scientific reasoning "
            "authority. Think and act at the research-program level, not as a one-call-at-a-time executor. "
            "You may author multiple coherent Research Packages in one decision and multiple Analysis "
            "Specifications inside each package. Author every scientifically justified analysis that can be "
            "specified now without seeing an unknown future result. When later scientific work genuinely depends "
            "on an unknown result, stop that branch at an explicit decision boundary instead of guessing the future. "
            "You own questions, hypotheses, evidence choice, variables, representations, transformations, methods, "
            "scientifically meaningful parameters, horizons, thresholds, interactions, regimes, interpretation, "
            "significance, findings, RP boundaries, RP closure, and subject continuation. Deterministic code is a "
            "compiler/executor only. It resolves generated request/result identities, exact output paths, and internal "
            "input aliases. Do not author result_id, output_path, request_id, or executor input aliases for new work. "
            "Refer to acquired evidence by exact evidence_id and prior work by stable logical analysis_id. A logical "
            "analysis_id may refer to an earlier analysis in the current batch or to a completed analysis advertised "
            "in campaign_analysis_result_catalog from an earlier batch. Each input has a semantic role. Inside method "
            "parameters, use that role wherever an executor contract asks for input_name; the compiler replaces the "
            "role with the exact runtime binding. A prior analysis input may omit dataset_name only when you intend its "
            "sole reusable derived dataset; if several reusable datasets are scientifically possible, name the intended "
            "dataset. Deterministic code may resolve only semantics-preserving mechanics and may never invent or "
            "substitute science. Independent branches should be planned together when scientifically useful. Return "
            "exactly one batch decision JSON object and no prose."
        )
        schema = {
            "continue_research": "boolean",
            "research_packages": [
                {
                    "rp_id": "nonblank stable string",
                    "parent_rp_id": "different prior/local rp_id or null",
                    "objective": "scientific objective",
                    "decision_boundary": (
                        "string or null describing what unknown result must return to RD before contingent science"
                    ),
                    "analyses": [
                        {
                            "analysis_id": "stable logical identifier unique across the campaign",
                            "rp_id": "same as containing rp_id",
                            "question_id": "stable scientific question identifier",
                            "parent_question_id": "different prior question_id or null",
                            "parent_rp_id": "different parent RP or null",
                            "subject_id": "active subject_id",
                            "question": "scientific question",
                            "method_id": "exact available method_id selected by RD",
                            "inputs": [
                                {
                                    "role": "semantic role used by method parameters when input_name is needed",
                                    "evidence_id": "exact acquired evidence_id or null",
                                    "analysis_id": "logical prior/current analysis_id or null",
                                    "dataset_name": "named reusable derived dataset or null",
                                }
                            ],
                            "parameters": "scientifically meaningful method parameters; use semantic roles for input_name fields",
                            "research_phase": "EXPLORATION or VALIDATION",
                            "rationale": "scientific rationale",
                        }
                    ],
                }
            ],
            "rp_closures": [
                {
                    "rp_id": "exact open RP judged scientifically complete",
                    "close_reason": "nonblank scientific reason this RP is complete",
                    "final_assessment": "integrated scientific assessment or null",
                }
            ],
            "promote_findings": [
                {
                    "finding_id": "string",
                    "subject_id": "string",
                    "statement": "string",
                    "supporting_result_ids": ["exact result IDs already returned in completed batch reports"],
                    "evidence_ids": ["string"],
                    "metadata": "open-ended scientific object",
                }
            ],
            "research_state": "open-ended cumulative AI-authored scientific state",
            "batch_interpretation": (
                "substantive integrated interpretation of the completed batch on INTERPRET_BATCH_RESULTS; otherwise null allowed"
            ),
            "close_reason": "nonblank subject-level scientific reason when continue_research=false, otherwise null",
        }
        instructions = [
            "Do not serialize low-level request_id, result_id, output_path, or executor alias plumbing for new analyses.",
            "Create several Research Packages in the same batch when materially distinct scientific propositions are worth testing now.",
            "Within each RP, include every analysis whose justification is already available now; do not force one scalar test per RD turn.",
            "Use a prior logical analysis_id only for an actual dependency. Independent analyses should not be artificially chained.",
            "A follow-up batch may reference a completed prior analysis by its stable logical analysis_id from campaign_analysis_result_catalog; never copy its generated result_id/output_path into a new scientific specification.",
            "Never reuse an analysis_id for a new execution. A new analysis attempt requires a new logical analysis_id even when it addresses the same question.",
            "Do not author contingent follow-up analyses whose scientific justification depends on an unknown result. Describe that stopping point in decision_boundary and wait for the consolidated batch report.",
            "Select exact methods and scientifically meaningful parameters yourself from context.available_analysis_methods.",
            "Choosing whether datasets should be aligned, the scientific alignment key/mode, selected columns, transformations, horizons, thresholds, and outcomes remains your responsibility.",
            "Internal names are not scientific authority. Use input semantic roles in alignment[].input_name and selections[].input_name; the compiler resolves them.",
            "On INTERPRET_BATCH_RESULTS, interpret the completed batch as a scientific whole before issuing follow-up work. Follow-up may include multiple RPs and multiple analyses again.",
            "Use rp_closures to close every RP you judge scientifically exhausted. Closing an RP is not the same as closing the subject; in the same decision you may close exhausted RPs and open or continue other RPs.",
            "Do not keep an RP artificially open merely because subject-level research continues, and do not close the subject merely because one RP is exhausted.",
            "Promote only findings you judge significant. The compiler/executor never decides scientific significance.",
            "A failure in one batch branch does not imply the other scientific branches failed; interpret each returned record on its evidence.",
            "During EXPLORATION actively seek predictive structure at T -> T+1 onward without manufacturing positive findings. During VALIDATION preserve all governing no-look-ahead restrictions.",
        ]
        user = {
            "operation": operation,
            "mission": mission,
            "required_batch_decision_schema": schema,
            "instructions": instructions,
            "context": payload,
        }
        return [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(user, sort_keys=True, default=str, separators=(",", ":")),
            },
        ]

    def _request_batch_decision(
        self,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> BatchResearchDecision:
        messages = self._batch_messages(operation=operation, mission=mission, payload=payload)
        content = self._chat_completion(messages)
        defect: str | None = None
        try:
            decision = BatchResearchDecisionCodec.decode(content)
            defect = self._batch_phase_defect(decision)
            if defect is None:
                return decision
        except BatchResearchDecisionDecodeError as exc:
            defect = str(exc)

        assistant_content = content
        for _ in range(self._MAX_BATCH_REPRESENTATION_REPAIRS):
            repaired = self._chat_completion(
                messages
                + [
                    {"role": "assistant", "content": assistant_content},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "operation": "REPAIR_BATCH_DECISION_REPRESENTATION",
                                "decode_defect": defect,
                                "instruction": (
                                    "Return one complete corrected batch decision JSON object. Correct only the "
                                    "objective representation/phase defect. Preserve or revise your scientific plan "
                                    "as you judge appropriate. Deterministic code will not invent scientific content."
                                ),
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    },
                ]
            )
            assistant_content = repaired
            try:
                decision = BatchResearchDecisionCodec.decode(repaired)
            except BatchResearchDecisionDecodeError as exc:
                defect = str(exc)
                continue
            defect = self._batch_phase_defect(decision)
            if defect is None:
                return decision
        raise ValueError("batch decision representation repair budget exhausted: " + str(defect))

    def _batch_phase_defect(self, decision: BatchResearchDecision) -> str | None:
        if self._required_subject_id is None and self._required_research_phase is None:
            return None
        for package in decision.research_packages:
            for analysis in package.analyses:
                if self._required_subject_id is not None and analysis.subject_id != self._required_subject_id:
                    return (
                        f"analysis {analysis.analysis_id} subject_id violates active subject contract: "
                        f"required {self._required_subject_id}, received {analysis.subject_id}"
                    )
                if (
                    self._required_research_phase is not None
                    and analysis.research_phase is not self._required_research_phase
                ):
                    return (
                        f"analysis {analysis.analysis_id} research_phase violates active subject phase contract: "
                        f"required {self._required_research_phase.value}, received {analysis.research_phase.value}"
                    )
        return None

    @classmethod
    def _report_payload(cls, report: BatchExecutionReport) -> Mapping[str, object]:
        records = []
        for record in report.records:
            item: dict[str, object] = {
                "analysis_id": record.analysis_id,
                "rp_id": record.rp_id,
                "status": record.status,
                "objective_defect": record.objective_defect,
                "binding_map": dict(record.binding_map),
                "mechanical_repairs": list(record.mechanical_repairs),
            }
            if record.compiled_request is not None:
                item["compiled_request_audit"] = {
                    "request_id": record.compiled_request.request_id,
                    "method_id": record.compiled_request.method_id,
                    "question_id": record.compiled_request.question_id,
                    "rp_id": record.compiled_request.rp_id,
                }
            if record.result is not None:
                item["analysis_result"] = cls._analysis_result_payload(record.result)
            records.append(item)
        return {"records": records}
