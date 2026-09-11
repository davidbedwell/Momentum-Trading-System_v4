from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .batch_contracts import BatchExecutionReport, BatchResearchDecision, ResearchPackagePlan
from .contracts import AnalysisRequest, SubjectMetadata
from .research_package import ResearchAnalysisRecord, ResearchPackage, ResearchQuestionRecord
from .research_package_store import JsonResearchPackageStore


class BatchResearchRecordingError(RuntimeError):
    pass


class BatchCampaignResearchRecorder:
    """Persist batched AI-authored RP structure without inventing scientific content.

    A batch decision is recorded before Analysis execution so every AI-authored RP
    and question exists independently of executor ordering. Exact compiled requests
    are appended later after objective validation. Result outcomes and explicit RP
    closures are then attached mechanically from the batch report/decision.
    """

    def __init__(self, *, package_store: JsonResearchPackageStore) -> None:
        self._packages = package_store

    def record_plan(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        decision: BatchResearchDecision,
    ) -> None:
        for plan in decision.research_packages:
            self._record_package_plan(
                campaign_id=campaign_id,
                subject=subject,
                plan=plan,
            )

    def _record_package_plan(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        plan: ResearchPackagePlan,
    ) -> None:
        package = self._packages.load(plan.rp_id)
        if package is None:
            package = ResearchPackage(
                rp_id=plan.rp_id,
                subject_id=subject.subject_id,
                campaign_id=campaign_id,
                parent_rp_id=plan.parent_rp_id,
                originating_question=plan.objective,
                originating_rationale=plan.decision_boundary or plan.objective,
            )
            self._packages.create(package)
        else:
            if package.subject_id != subject.subject_id:
                raise BatchResearchRecordingError(
                    f"Research Package belongs to another subject: {plan.rp_id}"
                )
            if package.campaign_id != campaign_id:
                raise BatchResearchRecordingError(
                    f"Research Package belongs to another campaign: {plan.rp_id}"
                )
            if package.status != "OPEN":
                raise BatchResearchRecordingError(
                    f"closed Research Package cannot receive new analyses: {plan.rp_id}"
                )
            if package.parent_rp_id != plan.parent_rp_id:
                raise BatchResearchRecordingError(
                    f"Research Package parent changed: {plan.rp_id}"
                )

        existing_question_ids = {item.question_id for item in package.questions}
        pending = {
            analysis.question_id: analysis
            for analysis in plan.analyses
            if analysis.question_id not in existing_question_ids
        }
        if len(pending) != len(
            {
                analysis.question_id
                for analysis in plan.analyses
                if analysis.question_id not in existing_question_ids
            }
        ):
            raise BatchResearchRecordingError(
                f"duplicate question_id definitions in Research Package plan: {plan.rp_id}"
            )

        evolved = package
        while pending:
            ready = [
                item
                for item in pending.values()
                if item.parent_question_id is None
                or item.parent_question_id in existing_question_ids
            ]
            if not ready:
                unresolved = {
                    question_id: item.parent_question_id
                    for question_id, item in pending.items()
                }
                raise BatchResearchRecordingError(
                    f"question lineage cannot be resolved in {plan.rp_id}: {unresolved}"
                )
            for analysis in ready:
                evolved = evolved.append_question(
                    ResearchQuestionRecord(
                        question_id=analysis.question_id,
                        parent_question_id=analysis.parent_question_id,
                        question=analysis.question,
                        rationale=analysis.rationale,
                        research_phase=analysis.research_phase.value,
                    )
                )
                existing_question_ids.add(analysis.question_id)
                pending.pop(analysis.question_id)

        if evolved is not package:
            self._packages.save(evolved)

    def record_accepted_request(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
    ) -> None:
        if not request.rp_id or not request.question_id:
            raise BatchResearchRecordingError("compiled request lacks rp_id/question_id lineage")
        package = self._packages.load(request.rp_id)
        if package is None:
            raise BatchResearchRecordingError(
                f"compiled request references an unrecorded Research Package: {request.rp_id}"
            )
        if package.campaign_id != campaign_id or package.subject_id != subject.subject_id:
            raise BatchResearchRecordingError("compiled request campaign/subject lineage mismatch")
        if not any(item.question_id == request.question_id for item in package.questions):
            raise BatchResearchRecordingError(
                f"compiled request references an unrecorded question: {request.question_id}"
            )
        if any(item.request_id == request.request_id for item in package.analyses):
            return
        evolved = package.append_analysis(
            ResearchAnalysisRecord(
                request_id=request.request_id,
                question_id=request.question_id,
                method_id=request.method_id,
                parameters=dict(request.parameters),
                evidence_ids=tuple(request.evidence_ids),
                analysis_inputs=tuple(asdict(item) for item in request.analysis_inputs),
                research_phase=request.research_phase.value,
            )
        )
        self._packages.save(evolved)

    def record_report(self, report: BatchExecutionReport) -> None:
        for record in report.records:
            if record.compiled_request is None or record.result is None:
                continue
            package = self._packages.load(record.rp_id)
            if package is None:
                raise BatchResearchRecordingError(
                    f"batch result references missing Research Package: {record.rp_id}"
                )
            future = record.result.execution_metadata.get("future_information", {})
            future_mapping = future if isinstance(future, dict) else {"value": future}
            evolved = package.record_analysis_outcome(
                request_id=record.compiled_request.request_id,
                result_id=record.result.result_id,
                execution_status=record.result.execution_metadata.get("execution_status"),
                interpretation=None,
                future_information=future_mapping,
            )
            self._packages.save(evolved)

    def record_closures(self, decision: BatchResearchDecision) -> None:
        for closure in decision.rp_closures:
            package = self._packages.load(closure.rp_id)
            if package is None:
                raise BatchResearchRecordingError(
                    f"RP closure references missing package: {closure.rp_id}"
                )
            if package.status == "CLOSED":
                continue
            self._packages.save(
                package.close(
                    close_reason=closure.close_reason,
                    final_assessment=closure.final_assessment,
                )
            )
