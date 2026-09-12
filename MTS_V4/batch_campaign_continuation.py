from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .batch_compiler import BatchCompilationError, BatchCompilerContext, topological_analysis_order
from .batch_contracts import BatchAnalysisRecord, BatchExecutionReport, BatchResearchDecision
from .batch_orchestrator import (
    AcceptedRequestCallback,
    BatchDecisionCallback,
    BatchReportCallback,
    BatchResearchLoopError,
    BatchResearchLoopOrchestrator,
    BatchResearchLoopOutcome,
)
from .contracts import AnalysisResult, EvidenceDescriptor, SubjectMetadata


@dataclass(frozen=True, slots=True)
class ContinuationBaseline:
    decisions: int
    batches_executed: int
    analyses_executed: int
    findings_promoted: int = 0


class RecoveredBatchCampaignContinuation(BatchResearchLoopOrchestrator):
    """Continue from one already accepted AI-authored batch decision.

    The recovered campaign's prior Analysis results are seeded by stable logical
    analysis_id. They are available to the compiler as dependencies but are never
    re-executed. The first executable work is exactly the Analysis Specifications
    in ``initial_decision``. Every later batch is authored by the AI Research
    Director after receiving the consolidated preceding report.
    """

    def continue_from_decision(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        initial_decision: BatchResearchDecision,
        prior_results_by_analysis_id: Mapping[str, AnalysisResult],
        baseline: ContinuationBaseline,
        decision_callback: BatchDecisionCallback | None = None,
        report_callback: BatchReportCallback | None = None,
        accepted_request_callback: AcceptedRequestCallback | None = None,
    ) -> BatchResearchLoopOutcome:
        if baseline.decisions < 1:
            raise BatchResearchLoopError("continuation baseline must include at least one prior decision")
        if not initial_decision.continue_research:
            return BatchResearchLoopOutcome(
                decisions=baseline.decisions,
                batches_executed=baseline.batches_executed,
                analyses_executed=baseline.analyses_executed,
                findings_promoted=baseline.findings_promoted,
                closed=True,
                close_reason=initial_decision.close_reason,
                final_decision=initial_decision,
                last_report=None,
            )

        self._nexus.upsert_subject(subject)
        evidence_map = {item.evidence_id: item for item in evidence}
        if len(evidence_map) != len(evidence):
            raise BatchResearchLoopError("duplicate evidence_id")
        for item in evidence:
            if item.subject_id != subject.subject_id:
                raise BatchResearchLoopError(
                    f"evidence {item.evidence_id} does not belong to {subject.subject_id}"
                )
            self._nexus.upsert_evidence_metadata(item.durable_metadata())

        results_by_analysis_id = dict(prior_results_by_analysis_id)
        if len(results_by_analysis_id) != len(prior_results_by_analysis_id):
            raise BatchResearchLoopError("duplicate recovered analysis_id")
        for analysis_id, result in results_by_analysis_id.items():
            if result.subject_id != subject.subject_id:
                raise BatchResearchLoopError(
                    f"recovered result {analysis_id} belongs to {result.subject_id}, not {subject.subject_id}"
                )

        decisions = baseline.decisions
        batches = baseline.batches_executed
        analyses = baseline.analyses_executed
        promoted = baseline.findings_promoted
        decision = initial_decision
        last_report: BatchExecutionReport | None = None

        while decision.continue_research:
            specifications = self._flatten_and_validate_decision(decision, subject)
            prior_analysis_ids = set(results_by_analysis_id)
            duplicate_ids = sorted(
                specification.analysis_id
                for specification in specifications
                if specification.analysis_id in prior_analysis_ids
            )
            if duplicate_ids:
                raise BatchResearchLoopError(
                    "recovered continuation attempted to re-execute prior analysis_id(s): "
                    + ", ".join(duplicate_ids)
                )

            try:
                ordered = topological_analysis_order(specifications)
            except BatchCompilationError as exc:
                last_report = BatchExecutionReport(
                    records=(
                        BatchAnalysisRecord(
                            analysis_id="__batch_plan__",
                            rp_id="__batch_plan__",
                            status="AMBIGUOUS_SCIENTIFIC_REPAIR_REQUIRED",
                            objective_defect=str(exc),
                        ),
                    )
                )
                self._notify_report(report_callback, last_report, decisions, analyses)
                decision = self._rd.interpret_batch_results(
                    mission=self._mission,
                    subject=subject,
                    prior_decision=decision,
                    report=last_report,
                    evidence=evidence,
                    available_methods=self._available_methods,
                    nexus_context=self._nexus_context(subject.subject_id, results_by_analysis_id),
                )
                decisions += 1
                promoted += self._publish_promotions(decision)
                self._notify_decision(decision_callback, decision, decisions, analyses)
                continue

            records: list[BatchAnalysisRecord] = []
            failed_analysis_ids: set[str] = set()
            current_batch_results: dict[str, AnalysisResult] = {}

            for specification in ordered:
                dependency_ids = {
                    ref.analysis_id
                    for ref in specification.inputs
                    if ref.analysis_id is not None
                }
                failed_dependencies = sorted(
                    dep for dep in dependency_ids if dep in failed_analysis_ids
                )
                if failed_dependencies:
                    failed_analysis_ids.add(specification.analysis_id)
                    records.append(
                        BatchAnalysisRecord(
                            analysis_id=specification.analysis_id,
                            rp_id=specification.rp_id,
                            status="BLOCKED_DEPENDENCY",
                            objective_defect=(
                                "upstream batch dependency did not complete successfully: "
                                + ", ".join(failed_dependencies)
                            ),
                        )
                    )
                    continue

                compiler_results = dict(results_by_analysis_id)
                compiler_results.update(current_batch_results)
                try:
                    compiled = self._compiler.compile(
                        specification,
                        context=BatchCompilerContext(
                            evidence=evidence_map,
                            results_by_analysis_id=compiler_results,
                        ),
                    )
                except BatchCompilationError as exc:
                    failed_analysis_ids.add(specification.analysis_id)
                    records.append(
                        BatchAnalysisRecord(
                            analysis_id=specification.analysis_id,
                            rp_id=specification.rp_id,
                            status="AMBIGUOUS_SCIENTIFIC_REPAIR_REQUIRED",
                            objective_defect=str(exc),
                        )
                    )
                    continue

                request = compiled.request
                defects = self._validator.validate(
                    request,
                    evidence_map,
                    {result.result_id: result for result in compiler_results.values()},
                )
                if defects:
                    failed_analysis_ids.add(specification.analysis_id)
                    records.append(
                        BatchAnalysisRecord(
                            analysis_id=specification.analysis_id,
                            rp_id=specification.rp_id,
                            status="OBJECTIVE_CONTRACT_DEFECT",
                            compiled_request=request,
                            objective_defect="; ".join(defect.message for defect in defects),
                            binding_map=compiled.binding_map,
                            mechanical_repairs=compiled.mechanical_repairs,
                        )
                    )
                    continue

                if accepted_request_callback is not None:
                    accepted_request_callback(request)

                payloads: dict[str, object] = {}
                for evidence_id in request.evidence_ids:
                    descriptor = evidence_map[evidence_id]
                    payloads[evidence_id] = self._cache.get(descriptor.cache_key)
                result_index = {result.result_id: result for result in compiler_results.values()}
                for reference in request.analysis_inputs:
                    source_result = result_index[reference.result_id]
                    payloads[reference.input_name] = self._validator.resolve_analysis_input(
                        reference,
                        source_result,
                    )

                result = self._analysis.execute(request, payloads)
                analyses += 1
                result = self._enrich_result_lineage(
                    request=request,
                    result=result,
                    result_index=result_index,
                )
                self._nexus.register_analysis_result_metadata(result.durable_metadata())
                current_batch_results[specification.analysis_id] = result
                results_by_analysis_id[specification.analysis_id] = result

                status = str(result.execution_metadata.get("execution_status", "UNKNOWN"))
                if status != "SUCCESS":
                    failed_analysis_ids.add(specification.analysis_id)
                records.append(
                    BatchAnalysisRecord(
                        analysis_id=specification.analysis_id,
                        rp_id=specification.rp_id,
                        status=status,
                        compiled_request=request,
                        result=result,
                        binding_map=compiled.binding_map,
                        mechanical_repairs=compiled.mechanical_repairs,
                    )
                )

            batches += 1
            last_report = BatchExecutionReport(records=tuple(records))
            self._notify_report(report_callback, last_report, decisions, analyses)

            decision = self._rd.interpret_batch_results(
                mission=self._mission,
                subject=subject,
                prior_decision=decision,
                report=last_report,
                evidence=evidence,
                available_methods=self._available_methods,
                nexus_context=self._nexus_context(subject.subject_id, results_by_analysis_id),
            )
            decisions += 1
            promoted += self._publish_promotions(decision)
            self._notify_decision(decision_callback, decision, decisions, analyses)

        return BatchResearchLoopOutcome(
            decisions=decisions,
            batches_executed=batches,
            analyses_executed=analyses,
            findings_promoted=promoted,
            closed=True,
            close_reason=decision.close_reason,
            final_decision=decision,
            last_report=last_report,
        )
