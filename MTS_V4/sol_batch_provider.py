from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any, Mapping, Sequence

from .batch_contracts import BatchExecutionReport, BatchResearchDecision
from .batch_rd_codec import BatchResearchDecisionCodec, BatchResearchDecisionDecodeError
from .contracts import EvidenceDescriptor, SubjectMetadata
from .sol_primary_provider import SolPrimaryResearchDirector
from .sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    HumanSpendAuthorizationCallback,
)


class SolBatchResearchDirector(SolPrimaryResearchDirector):
    """Program-level Sol RD for unbounded scientific batches with human spend control."""

    _MAX_BATCH_REPRESENTATION_REPAIRS = 2

    def __init__(
        self,
        *args,
        sol_spend_limit_usd: float = DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        human_spend_authorization_callback: HumanSpendAuthorizationCallback | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.configure_sol_spend_guard(
            authorized_spend_usd=sol_spend_limit_usd,
            authorization_callback=human_spend_authorization_callback,
        )

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
        spend_snapshot = self.sol_spend_snapshot()
        if spend_snapshot is not None:
            payload["human_sol_spend_context"] = {
                "authorized_spend_usd": spend_snapshot.authorized_spend_usd,
                "actual_spend_usd": spend_snapshot.actual_spend_usd,
                "authority": (
                    "Operational information only. Do not alter scientific breadth to fit this dollar amount. "
                    "Estimate scientific work remaining independently; deterministic/human controls decide funding."
                ),
            }
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
            "At each decision point, create or continue as many Research Packages as you judge scientifically "
            "relevant to the research objective and include all scientifically justified lines of inquiry that can "
            "be specified from the evidence currently available. Zero, one, or many Research Packages may be "
            "scientifically appropriate; never target a preferred count. Within each RP, author every scientifically "
            "justified Analysis Specification that can be specified now without seeing an unknown future result. "
            "When later scientific work genuinely depends on an unknown result, stop that branch at an explicit "
            "decision boundary instead of guessing the future. You own questions, hypotheses, evidence choice, "
            "variables, representations, transformations, methods, scientifically meaningful parameters, horizons, "
            "thresholds, interactions, regimes, interpretation, significance, findings, RP boundaries, RP closure, "
            "and subject continuation. Deterministic code is a compiler/executor only. It resolves generated "
            "request/result identities, exact output paths, and internal input aliases. Do not author result_id, "
            "output_path, request_id, or executor input aliases for new work. Refer to acquired evidence by exact "
            "evidence_id and prior work by stable logical analysis_id. A logical analysis_id may refer to an earlier "
            "analysis in the current batch or to a completed analysis advertised in campaign_analysis_result_catalog "
            "from an earlier batch. Each input has a semantic role. Inside method parameters, use that role wherever "
            "an executor contract asks for input_name; the compiler replaces the role with the exact runtime binding. "
            "A prior analysis input may omit dataset_name only when you intend its sole reusable derived dataset; if "
            "several reusable datasets are scientifically possible, name the intended dataset. Deterministic code may "
            "resolve only semantics-preserving mechanics and may never invent or substitute science. The central "
            "scientific purpose during EXPLORATION is prospective predictive discovery: seek falsifiable relationships "
            "between information observable at T and subsequent direction, magnitude, timing, continuation or reversal, "
            "and path quality at T+1 onward. Historical look-ahead is legitimate during EXPLORATION when scientifically "
            "useful for discovery; do not manufacture positive claims and reject unsupported candidates. VALIDATION is "
            "different: preserve the no-look-ahead boundary at prediction time. When cross-subject scientific memory is "
            "present, treat it as prior scientific experience rather than a mandatory agenda. Test, challenge, "
            "reformulate, condition, defer, or ignore it as scientifically appropriate. Do not inherit a prior threshold, "
            "lookback, horizon, method, target, or representation merely for consistency. A negative result for one "
            "formulation does not prove that the subject lacks predictive structure. Historical rp_id values appearing "
            "only in cross-subject memory are provenance, not active local parent Research Packages. Distinguish "
            "exhaustion of one RP from exhaustion of useful work on the subject. At every decision, independently estimate "
            "scientific progress and remaining work. The funding ceiling is operational context only: never reduce, rank, "
            "suppress, or reshape scientifically justified work to fit it. Return exactly one batch decision JSON object "
            "and no prose."
        )
        schema = {
            "continue_research": "boolean",
            "research_packages": [
                {
                    "rp_id": "nonblank stable string",
                    "parent_rp_id": "different active local/same-batch rp_id or null",
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
                            "parent_rp_id": "same lineage parent as containing RP or null",
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
                    "rp_id": "exact previously open local RP judged scientifically complete",
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
            "research_state": {
                "other_state": "arbitrary cumulative AI-authored scientific state",
                "predictive_hypothesis_updates": [
                    {
                        "rp_id": "exact active local RP",
                        "action": "CREATE_TENTATIVE, LOCK_VALIDATION_TRIAL, or RECORD_VALIDATION_OUTCOME",
                        "hypothesis_id": "stable string",
                        "statement": "CREATE_TENTATIVE only: frozen predictive proposition",
                        "success_definition": "CREATE_TENTATIVE only: predeclared objective success condition",
                        "minimum_required_trials": "CREATE_TENTATIVE only: positive integer selected before blind testing",
                        "source_result_ids": "CREATE_TENTATIVE only: supporting result IDs already completed in that RP",
                        "trial_id": "LOCK_VALIDATION_TRIAL/RECORD_VALIDATION_OUTCOME only",
                        "prediction_result_id": "LOCK_VALIDATION_TRIAL only: exact completed no-lookahead VALIDATION result ID",
                        "prediction_statement": "LOCK_VALIDATION_TRIAL only: exact prediction frozen before outcome exposure",
                        "outcome_result_id": "RECORD_VALIDATION_OUTCOME only: exact completed outcome result ID",
                        "success": "RECORD_VALIDATION_OUTCOME only: boolean judged against frozen success_definition",
                    }
                ],
            },
            "research_progress": {
                "estimated_percent_complete": "number from 0 through 100 based on your scientific assessment",
                "estimated_remaining_batches": (
                    "nonnegative integer; when continuing, include the Analysis batch authorized by this decision "
                    "plus any additional batches you currently expect"
                ),
                "estimated_remaining_sol_calls": (
                    "nonnegative integer number of future Sol decisions you currently expect after this decision, "
                    "including interpretation of the batch authorized here when continuing"
                ),
                "estimate_confidence": "nonblank confidence statement such as low, medium, or high",
                "estimate_rationale": (
                    "brief scientific explanation of what remains unresolved and why that amount of work is expected"
                ),
            },
            "batch_interpretation": (
                "substantive integrated interpretation of the completed batch on INTERPRET_BATCH_RESULTS; otherwise null allowed"
            ),
            "close_reason": "nonblank subject-level scientific reason when continue_research=false, otherwise null",
        }
        instructions = [
            "Do not serialize low-level request_id, result_id, output_path, or executor alias plumbing for new analyses.",
            "Create or continue as many Research Packages as are scientifically relevant now; include all currently justified lines of inquiry and do not target any preferred RP count.",
            "Within each RP, include every analysis whose justification is already available now; do not force one scalar test per RD turn.",
            "Use a prior logical analysis_id only for an actual dependency. Independent analyses should not be artificially chained.",
            "A follow-up batch may reference a completed prior analysis by its stable logical analysis_id from campaign_analysis_result_catalog; never copy its generated result_id/output_path into a new scientific specification.",
            "Never reuse an analysis_id for a new execution. A new analysis attempt requires a new logical analysis_id even when it addresses the same question.",
            "Do not author contingent follow-up analyses whose scientific justification depends on an unknown result. Describe that stopping point in decision_boundary and wait for the consolidated batch report.",
            "Select exact methods and scientifically meaningful parameters yourself from context.available_analysis_methods.",
            "Choosing whether datasets should be aligned, the scientific alignment key/mode, selected columns, transformations, horizons, thresholds, and outcomes remains your responsibility.",
            "Internal names are not scientific authority. Use input semantic roles in alignment[].input_name and selections[].input_name; the compiler resolves them.",
            "On INTERPRET_BATCH_RESULTS, interpret the completed batch as a scientific whole before issuing follow-up work. Follow-up may contain zero, one, or many RPs and Analysis Specifications as scientifically warranted.",
            "Provide research_progress on every decision. Estimate scientific completion and remaining work independently of the human funding ceiling; never trim science to make the estimate fit the authorized dollars.",
            "When continue_research=true, estimated_remaining_batches and estimated_remaining_sol_calls must each be at least 1 because the current authorized Analysis batch and its later Sol interpretation remain ahead.",
            "When continue_research=false, estimated_remaining_batches and estimated_remaining_sol_calls must both be 0.",
            "Use rp_closures to close every previously open RP you judge scientifically exhausted. Do not close an RP in the same decision that schedules new analyses inside that RP; execute and interpret those analyses first.",
            "Closing an RP is not the same as closing the subject. In one interpretation you may close exhausted RPs and open or continue other RPs.",
            "Do not keep an RP artificially open merely because subject-level research continues, and do not close the subject merely because one RP is exhausted.",
            "A parent_rp_id must name an actual local RP for this subject, either already durable in context.research_packages or authored as another RP in this same batch. Historical RP identifiers from cross-subject memory are not local parents.",
            "For a continuing existing RP, preserve its durable parent_rp_id exactly. Analyses inside an RP must use the same parent_rp_id lineage as the containing RP.",
            "Promote only findings you judge significant. The compiler/executor never decides scientific significance.",
            "A failure in one batch branch does not imply the other scientific branches failed; interpret each returned record on its evidence.",
            "During EXPLORATION actively seek predictive structure at T -> T+1 onward without manufacturing positive findings. Historical look-ahead is a discovery capability, not a validation permission.",
            "During VALIDATION preserve the prediction-time no-look-ahead boundary and never generalize that restriction backward into EXPLORATION.",
            "Cross-subject memory is scientific context only. Do not assume generalization and do not let prior subjects delimit the discovery space.",
            "When exploration produces a relationship you judge potentially predictive, use research_state.predictive_hypothesis_updates action=CREATE_TENTATIVE with an exact rp_id, frozen proposition, objective success_definition, positive minimum_required_trials chosen before blind testing, and supporting completed source_result_ids.",
            "Predictive hypothesis definitions are frozen once created. A materially revised proposition requires a new hypothesis_id.",
            "For blind validation, lock predictions with action=LOCK_VALIDATION_TRIAL only from a completed VALIDATION result that contains no future information. Lock the prediction before any outcome/future information is exposed.",
            "Record a validation outcome with action=RECORD_VALIDATION_OUTCOME only after the trial is already locked. The deterministic persistence layer calculates cumulative counts/rates/status under the existing human-approved verification rule; you retain scientific authority over hypothesis, prediction, trial design, success definition, and success judgment.",
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
            defect = self._batch_decision_defect(decision)
            if defect is None:
                return self._accept_batch_decision(decision)
        except BatchResearchDecisionDecodeError as exc:
            defect = str(exc)

        assistant_content = content
        for repair_index in range(self._MAX_BATCH_REPRESENTATION_REPAIRS):
            self._write_telemetry(
                {
                    "event": "BATCH_DECISION_REPRESENTATION_DEFECT",
                    "operation": operation,
                    "repair_attempt": repair_index + 1,
                    "decode_defect": defect,
                }
            )
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
                                    "objective representation/phase/identity/progress-estimate defect. Preserve or "
                                    "revise your scientific plan as you judge appropriate. Deterministic code will "
                                    "not invent scientific content or alter your research breadth."
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
            defect = self._batch_decision_defect(decision)
            if defect is None:
                return self._accept_batch_decision(decision)
        self._write_telemetry(
            {
                "event": "BATCH_DECISION_REPRESENTATION_REPAIR_EXHAUSTED",
                "operation": operation,
                "repair_attempts": self._MAX_BATCH_REPRESENTATION_REPAIRS,
                "decode_defect": defect,
            }
        )
        raise ValueError("batch decision representation repair budget exhausted: " + str(defect))

    def _accept_batch_decision(self, decision: BatchResearchDecision) -> BatchResearchDecision:
        assert decision.research_progress is not None
        self.update_sol_research_progress(decision.research_progress)
        return decision

    def _batch_decision_defect(self, decision: BatchResearchDecision) -> str | None:
        defect = self._batch_phase_defect(decision)
        if defect is not None:
            return defect
        progress = decision.research_progress
        if progress is None:
            return "research_progress is required on every batched Sol decision"
        if decision.continue_research:
            if progress.estimated_remaining_batches < 1:
                return (
                    "continuing research requires research_progress.estimated_remaining_batches >= 1; "
                    "the Analysis batch authorized by this decision still remains"
                )
            if progress.estimated_remaining_sol_calls < 1:
                return (
                    "continuing research requires research_progress.estimated_remaining_sol_calls >= 1; "
                    "at least the later interpretation of this authorized batch remains"
                )
        else:
            if progress.estimated_remaining_batches != 0:
                return "closed research requires research_progress.estimated_remaining_batches=0"
            if progress.estimated_remaining_sol_calls != 0:
                return "closed research requires research_progress.estimated_remaining_sol_calls=0"
        return None

    def _batch_phase_defect(self, decision: BatchResearchDecision) -> str | None:
        batch_packages = {package.rp_id: package for package in decision.research_packages}
        for package in decision.research_packages:
            if package.parent_rp_id == package.rp_id:
                return f"Research Package {package.rp_id} cannot be its own parent"
            if package.parent_rp_id is not None and package.parent_rp_id not in batch_packages:
                parent = self._research_package_store.load(package.parent_rp_id)
                if parent is None:
                    return (
                        f"Research Package {package.rp_id} parent_rp_id is not an active local RP: "
                        f"{package.parent_rp_id}. Historical/cross-subject RP identifiers are provenance only."
                    )
                if self._required_subject_id is not None and parent.subject_id != self._required_subject_id:
                    return (
                        f"Research Package {package.rp_id} parent belongs to another subject: "
                        f"{parent.subject_id}"
                    )
            existing = self._research_package_store.load(package.rp_id)
            if existing is not None:
                if existing.status != "OPEN":
                    return f"Research Package is already CLOSED and cannot receive new analyses: {package.rp_id}"
                if existing.parent_rp_id != package.parent_rp_id:
                    return (
                        f"Research Package {package.rp_id} parent_rp_id changed from durable lineage "
                        f"{existing.parent_rp_id!r} to {package.parent_rp_id!r}"
                    )
                if self._required_subject_id is not None and existing.subject_id != self._required_subject_id:
                    return f"Research Package {package.rp_id} belongs to another subject: {existing.subject_id}"

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
                if analysis.parent_rp_id != package.parent_rp_id:
                    return (
                        f"analysis {analysis.analysis_id} parent_rp_id must match containing RP lineage: "
                        f"expected {package.parent_rp_id!r}, received {analysis.parent_rp_id!r}"
                    )

        for closure in decision.rp_closures:
            if closure.rp_id in batch_packages:
                return (
                    f"RP {closure.rp_id} cannot be closed in the same decision that schedules new analyses "
                    "inside it; interpret those analyses first"
                )
            package = self._research_package_store.load(closure.rp_id)
            if package is None:
                return f"rp_closures references an unknown local RP: {closure.rp_id}"
            if package.status != "OPEN":
                return f"rp_closures references an RP that is already closed: {closure.rp_id}"
            if self._required_subject_id is not None and package.subject_id != self._required_subject_id:
                return f"rp_closures references an RP for another subject: {closure.rp_id}"

        raw_updates = decision.research_state.get("predictive_hypothesis_updates", [])
        if raw_updates not in (None, []):
            if not isinstance(raw_updates, list):
                return "research_state.predictive_hypothesis_updates must be a list"
            for update in raw_updates:
                if not isinstance(update, Mapping):
                    return "each predictive_hypothesis_updates entry must be an object"
                rp_id = update.get("rp_id")
                if not isinstance(rp_id, str) or not rp_id.strip():
                    return "each predictive_hypothesis_updates entry requires a nonblank rp_id"
                package = self._research_package_store.load(rp_id)
                if package is None:
                    return (
                        f"predictive hypothesis update references RP {rp_id!r} that is not yet durable. "
                        "Establish the RP through an executed batch first, then author the update in a later decision."
                    )
                if package.status != "OPEN":
                    return f"predictive hypothesis update references closed RP: {rp_id}"
                if self._required_subject_id is not None and package.subject_id != self._required_subject_id:
                    return f"predictive hypothesis update references another subject's RP: {rp_id}"
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
