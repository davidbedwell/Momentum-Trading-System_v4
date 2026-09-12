from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping, Protocol, Sequence

from .batch_compiler import (
    BatchCompilationError,
    BatchCompilerContext,
    ScientificSpecificationCompiler,
    topological_analysis_order,
)
from .batch_contracts import (
    BatchAnalysisRecord,
    BatchExecutionReport,
    BatchResearchDecision,
    ScientificAnalysisSpecification,
)
from .cache import TemporaryResearchCache
from .contracts import AnalysisRequest, AnalysisResult, EvidenceDescriptor, SubjectMetadata
from .interfaces import AnalysisExecutor
from .nexus import ResearchNexus
from .validation import ObjectiveContractValidator


class BatchResearchLoopError(RuntimeError):
    pass


class BatchResearchDirectorProvider(Protocol):
    def begin_batch_research(
        self,
        *,
        mission: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
    ) -> BatchResearchDecision: ...

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
    ) -> BatchResearchDecision: ...


AcceptedRequestCallback = Callable[[AnalysisRequest], None]
BatchDecisionCallback = Callable[[BatchResearchDecision, int, int], None]
BatchReportCallback = Callable[[BatchExecutionReport, int, int], None]


@dataclass(frozen=True, slots=True)
class BatchResearchLoopOutcome:
    decisions: int
    batches_executed: int
    analyses_executed: int
    findings_promoted: int
    closed: bool
    close_reason: str | None
    final_decision: BatchResearchDecision
    last_report: BatchExecutionReport | None = None


class BatchResearchLoopOrchestrator:
    """Program-level RD -> deterministic compile/execute batch -> RD loop.

    Scientific content comes only from the batch Research Director. The compiler
    resolves symbolic identities and executor bindings; it does not add analyses
    or scientific dependencies. Independent branches continue after branch-local
    objective defects so the RD receives one consolidated report.

    There is no deterministic scientific batch-size or analysis-count limit. Human
    Sol spending authorization is enforced at the premium-model transport boundary,
    where it cannot truncate, rank, or selectively execute a scientific batch.
    """

    def __init__(
        self,
        *,
        mission: str,
        rd: BatchResearchDirectorProvider,
        validator: ObjectiveContractValidator,
        analysis: AnalysisExecutor,
        nexus: ResearchNexus,
        cache: TemporaryResearchCache,
        available_methods: Sequence[Mapping[str, Any]],
        research_concepts: Sequence[Mapping[str, Any]] = (),
        compiler: ScientificSpecificationCompiler | None = None,
    ) -> None:
        self._mission = mission
        self._rd = rd
        self._validator = validator
        self._analysis = analysis
        self._nexus = nexus
        self._cache = cache
        self._available_methods = tuple(dict(method) for method in available_methods)
        self._research_concepts = tuple(dict(item) for item in research_concepts)
        self._compiler = compiler or ScientificSpecificationCompiler()

    def run(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        decision_callback: BatchDecisionCallback | None = None,
        report_callback: BatchReportCallback | None = None,
        accepted_request_callback: AcceptedRequestCallback | None = None,
    ) -> BatchResearchLoopOutcome:
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

        decisions = 0
        batches = 0
        analyses = 0
        promoted = 0
        results_by_analysis_id: dict[str, AnalysisResult] = {}

        decision = self._rd.begin_batch_research(
            mission=self._mission,
            subject=subject,
            evidence=evidence,
            available_methods=self._available_methods,
            nexus_context=self._nexus_context(subject.subject_id, results_by_analysis_id),
        )
        decisions += 1
        promoted += self._publish_promotions(decision)
        self._notify_decision(decision_callback, decision, decisions, analyses)
        last_report: BatchExecutionReport | None = None

        while decision.continue_research:
            specifications = self._flatten_and_validate_decision(decision, subject)
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

    @staticmethod
    def _flatten_and_validate_decision(
        decision: BatchResearchDecision,
        subject: SubjectMetadata,
    ) -> tuple[ScientificAnalysisSpecification, ...]:
        specifications: list[ScientificAnalysisSpecification] = []
        for package in decision.research_packages:
            if not package.analyses:
                raise BatchResearchLoopError(f"Research Package {package.rp_id} contains no analyses")
            for specification in package.analyses:
                if specification.rp_id != package.rp_id:
                    raise BatchResearchLoopError(
                        f"analysis {specification.analysis_id} RP mismatch: {specification.rp_id} != {package.rp_id}"
                    )
                if specification.subject_id != subject.subject_id:
                    raise BatchResearchLoopError(
                        f"analysis {specification.analysis_id} subject mismatch: "
                        f"{specification.subject_id} != {subject.subject_id}"
                    )
                specifications.append(specification)
        if not specifications:
            raise BatchResearchLoopError("continuing batch decision contains no Analysis Specifications")
        return tuple(specifications)

    def _enrich_result_lineage(
        self,
        *,
        request: AnalysisRequest,
        result: AnalysisResult,
        result_index: Mapping[str, AnalysisResult],
    ) -> AnalysisResult:
        if result.request_id != request.request_id:
            raise BatchResearchLoopError("Analysis result request lineage mismatch")
        if result.subject_id != request.subject_id:
            raise BatchResearchLoopError("Analysis result subject lineage mismatch")
        if result.method_id != request.method_id:
            raise BatchResearchLoopError("Analysis substituted a method")

        lineage_evidence_ids = list(request.evidence_ids)
        input_lineage: list[Mapping[str, object]] = []
        inherited_future: list[str] = []
        for reference in request.analysis_inputs:
            source = result_index[reference.result_id]
            for evidence_id in source.evidence_ids:
                if evidence_id not in lineage_evidence_ids:
                    lineage_evidence_ids.append(evidence_id)
            input_lineage.append(
                {
                    "input_name": reference.input_name,
                    "result_id": reference.result_id,
                    "output_path": list(reference.output_path),
                }
            )
            future = source.execution_metadata.get("future_information", {})
            if isinstance(future, Mapping) and future.get("contains_future_information"):
                inherited_future.append(reference.result_id)

        capability = next(
            (item for item in self._available_methods if item.get("method_id") == request.method_id),
            {},
        )
        direct_future = capability.get("allows_future_information") is True
        execution_metadata = dict(result.execution_metadata)
        if input_lineage:
            execution_metadata["analysis_input_lineage"] = input_lineage
        execution_metadata["future_information"] = {
            "contains_future_information": bool(direct_future or inherited_future),
            "direct_method_allows_future_information": direct_future,
            "inherited_from_result_ids": inherited_future,
            "policy": "MECHANICAL_TEMPORAL_LINEAGE_ONLY_RD_DECIDES_SCIENTIFIC_USE",
        }
        return replace(
            result,
            evidence_ids=tuple(lineage_evidence_ids),
            execution_metadata=execution_metadata,
        )

    def _publish_promotions(self, decision: BatchResearchDecision) -> int:
        for finding in decision.promote_findings:
            self._nexus.publish_finding(finding)
        return len(decision.promote_findings)

    @staticmethod
    def _notify_decision(
        callback: BatchDecisionCallback | None,
        decision: BatchResearchDecision,
        decisions: int,
        analyses: int,
    ) -> None:
        if callback is not None:
            callback(decision, decisions, analyses)

    @staticmethod
    def _notify_report(
        callback: BatchReportCallback | None,
        report: BatchExecutionReport,
        decisions: int,
        analyses: int,
    ) -> None:
        if callback is not None:
            callback(report, decisions, analyses)

    @staticmethod
    def _analysis_result_catalog(
        results_by_analysis_id: Mapping[str, AnalysisResult],
    ) -> tuple[Mapping[str, object], ...]:
        catalog: list[Mapping[str, object]] = []
        for analysis_id, result in results_by_analysis_id.items():
            reusable = result.outputs.get("derived_dataset_catalog", {})
            catalog.append(
                {
                    "analysis_id": analysis_id,
                    "result_id": result.result_id,
                    "request_id": result.request_id,
                    "method_id": result.method_id,
                    "execution_status": result.execution_metadata.get("execution_status"),
                    "reusable_derived_datasets": reusable if isinstance(reusable, Mapping) else {},
                    "future_information": result.execution_metadata.get("future_information", {}),
                }
            )
        return tuple(catalog)

    def _nexus_context(
        self,
        subject_id: str,
        results_by_analysis_id: Mapping[str, AnalysisResult],
    ) -> Mapping[str, object]:
        return {
            "subject": self._nexus.get_subject(subject_id),
            "evidence_metadata": self._nexus.evidence_metadata_for_subject(subject_id),
            "significant_findings": self._nexus.findings_for_subject(subject_id),
            "historical_analysis_result_metadata": self._nexus.analysis_result_metadata_for_subject(subject_id),
            "research_concepts": self._research_concepts,
            "research_concept_policy": {
                "authority": "NON_AUTHORITATIVE_IDEA_SEEDS",
                "treat_as_evidence": False,
                "rd_may_reject_or_reformulate": True,
                "rd_may_generate_additional_concepts": True,
                "deterministic_selection_or_ranking": False,
            },
            "campaign_analysis_result_catalog": self._analysis_result_catalog(results_by_analysis_id),
            "campaign_analysis_result_catalog_policy": {
                "persistence": "CAMPAIGN_LOCAL_NOT_NEXUS",
                "contains_row_payloads": False,
                "purpose": (
                    "Audit visibility. New batch Analysis Specifications should reference logical analysis_id, "
                    "not generated result_id/output_path plumbing."
                ),
            },
        }
