from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from .batch_contracts import BatchExecutionReport, BatchResearchDecision, ResearchPackagePlan
from .contracts import AnalysisRequest, SubjectMetadata
from .research_package import (
    PredictiveHypothesisRecord,
    PredictiveValidationTrialRecord,
    ResearchAnalysisRecord,
    ResearchPackage,
    ResearchQuestionRecord,
)
from .research_package_store import JsonResearchPackageStore


class BatchResearchRecordingError(RuntimeError):
    pass


class BatchCampaignResearchRecorder:
    """Persist batched AI-authored research structure without inventing science.

    Plans are recorded before execution, exact compiled requests after objective
    validation, objective results after execution, and AI-authored scientific
    updates only after the completed batch is available. Predictive hypothesis
    persistence preserves the same frozen-definition and blind-validation rules
    as the single-request compatibility path.
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
        """Persist RP plans in parent-safe order without changing scientific lineage."""
        pending = {plan.rp_id: plan for plan in decision.research_packages}
        if len(pending) != len(decision.research_packages):
            raise BatchResearchRecordingError("duplicate rp_id in batch plan")
        known = set(self._packages.list_ids())
        while pending:
            ready = [
                plan
                for plan in pending.values()
                if plan.parent_rp_id is None or plan.parent_rp_id in known
            ]
            if not ready:
                unresolved = {rp_id: plan.parent_rp_id for rp_id, plan in pending.items()}
                raise BatchResearchRecordingError(
                    f"Research Package parent lineage cannot be resolved: {unresolved}"
                )
            for plan in ready:
                self._record_package_plan(
                    campaign_id=campaign_id,
                    subject=subject,
                    plan=plan,
                )
                known.add(plan.rp_id)
                pending.pop(plan.rp_id)

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
        grouped: dict[str, Any] = {}
        for analysis in plan.analyses:
            prior = grouped.get(analysis.question_id)
            if prior is not None and (
                prior.question != analysis.question
                or prior.rationale != analysis.rationale
                or prior.parent_question_id != analysis.parent_question_id
                or prior.research_phase is not analysis.research_phase
            ):
                raise BatchResearchRecordingError(
                    f"question_id has conflicting scientific definitions in {plan.rp_id}: "
                    f"{analysis.question_id}"
                )
            grouped[analysis.question_id] = analysis
        pending = {
            question_id: analysis
            for question_id, analysis in grouped.items()
            if question_id not in existing_question_ids
        }

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
            future_mapping = future if isinstance(future, Mapping) else {"value": future}
            evolved = package.record_analysis_outcome(
                request_id=record.compiled_request.request_id,
                result_id=record.result.result_id,
                execution_status=record.result.execution_metadata.get("execution_status"),
                interpretation=None,
                future_information=future_mapping,
            )
            self._packages.save(evolved)

    @staticmethod
    def _require_nonblank(update: Mapping[str, Any], key: str) -> str:
        value = update.get(key)
        if not isinstance(value, str) or not value.strip():
            raise BatchResearchRecordingError(
                f"predictive hypothesis update requires nonblank {key}"
            )
        return value

    @staticmethod
    def _report_result_ids(report: BatchExecutionReport | None) -> set[str]:
        if report is None:
            return set()
        return {
            record.result.result_id
            for record in report.records
            if record.result is not None
        }

    def record_predictive_hypothesis_updates(
        self,
        decision: BatchResearchDecision,
        *,
        current_report: BatchExecutionReport | None,
    ) -> None:
        raw_updates = decision.research_state.get("predictive_hypothesis_updates", [])
        if raw_updates in (None, []):
            return
        if not isinstance(raw_updates, list):
            raise BatchResearchRecordingError(
                "research_state.predictive_hypothesis_updates must be a list"
            )
        current_result_ids = self._report_result_ids(current_report)
        packages: dict[str, ResearchPackage] = {}
        changed: set[str] = set()

        for raw in raw_updates:
            if not isinstance(raw, Mapping):
                raise BatchResearchRecordingError(
                    "each predictive hypothesis update must be an object"
                )
            rp_id = self._require_nonblank(raw, "rp_id")
            package = packages.get(rp_id) or self._packages.load(rp_id)
            if package is None:
                raise BatchResearchRecordingError(
                    f"predictive hypothesis update references unknown RP: {rp_id}"
                )
            if package.status != "OPEN":
                raise BatchResearchRecordingError(
                    f"predictive hypothesis update references closed RP: {rp_id}"
                )
            action = raw.get("action")
            if action == "CREATE_TENTATIVE":
                package = self._create_tentative_predictive_hypothesis(package, raw)
            elif action == "LOCK_VALIDATION_TRIAL":
                package = self._lock_predictive_validation_trial(
                    package,
                    raw,
                    current_result_ids=current_result_ids,
                )
            elif action == "RECORD_VALIDATION_OUTCOME":
                package = self._record_predictive_validation_outcome(
                    package,
                    raw,
                    current_result_ids=current_result_ids,
                )
            else:
                raise BatchResearchRecordingError(
                    f"unknown predictive hypothesis update action: {action!r}"
                )
            packages[rp_id] = package
            changed.add(rp_id)

        for rp_id in changed:
            self._packages.save(packages[rp_id])

    def _create_tentative_predictive_hypothesis(
        self,
        package: ResearchPackage,
        update: Mapping[str, Any],
    ) -> ResearchPackage:
        hypothesis_id = self._require_nonblank(update, "hypothesis_id")
        statement = self._require_nonblank(update, "statement")
        success_definition = self._require_nonblank(update, "success_definition")
        minimum_required_trials = update.get("minimum_required_trials")
        if (
            not isinstance(minimum_required_trials, int)
            or isinstance(minimum_required_trials, bool)
            or minimum_required_trials <= 0
        ):
            raise BatchResearchRecordingError(
                "CREATE_TENTATIVE requires positive integer minimum_required_trials"
            )
        source_result_ids = update.get("source_result_ids")
        if (
            not isinstance(source_result_ids, list)
            or not source_result_ids
            or not all(isinstance(value, str) and value.strip() for value in source_result_ids)
        ):
            raise BatchResearchRecordingError(
                "CREATE_TENTATIVE requires nonempty source_result_ids list"
            )

        source_analyses = []
        for result_id in source_result_ids:
            matches = [item for item in package.analyses if item.result_id == result_id]
            if len(matches) != 1:
                raise BatchResearchRecordingError(
                    f"predictive hypothesis source_result_id is not unique in RP: {result_id}"
                )
            source_analyses.append(matches[0])
        discovered_with_lookahead = any(
            bool(item.future_information.get("contains_future_information"))
            for item in source_analyses
        )

        existing = next(
            (
                item
                for item in package.predictive_hypotheses
                if item.hypothesis_id == hypothesis_id
            ),
            None,
        )
        if existing is not None:
            same_definition = (
                existing.statement == statement
                and existing.success_definition == success_definition
                and existing.minimum_required_trials == minimum_required_trials
                and existing.source_result_ids == tuple(source_result_ids)
            )
            if same_definition:
                return package
            raise BatchResearchRecordingError(
                f"predictive hypothesis definition is frozen; use a new hypothesis_id: {hypothesis_id}"
            )

        return package.append_predictive_hypothesis(
            PredictiveHypothesisRecord(
                hypothesis_id=hypothesis_id,
                statement=statement,
                success_definition=success_definition,
                minimum_required_trials=minimum_required_trials,
                source_result_ids=tuple(source_result_ids),
                discovered_with_lookahead=discovered_with_lookahead,
            )
        )

    def _lock_predictive_validation_trial(
        self,
        package: ResearchPackage,
        update: Mapping[str, Any],
        *,
        current_result_ids: set[str],
    ) -> ResearchPackage:
        hypothesis_id = self._require_nonblank(update, "hypothesis_id")
        trial_id = self._require_nonblank(update, "trial_id")
        prediction_result_id = self._require_nonblank(update, "prediction_result_id")
        prediction_statement = self._require_nonblank(update, "prediction_statement")
        if prediction_result_id not in current_result_ids:
            raise BatchResearchRecordingError(
                "LOCK_VALIDATION_TRIAL prediction_result_id must come from the immediately completed batch"
            )
        matches = [item for item in package.analyses if item.result_id == prediction_result_id]
        if len(matches) != 1:
            raise BatchResearchRecordingError(
                f"prediction result_id is not unique in RP: {prediction_result_id}"
            )
        analysis = matches[0]
        if analysis.research_phase != "VALIDATION":
            raise BatchResearchRecordingError(
                "LOCK_VALIDATION_TRIAL requires a VALIDATION prediction analysis"
            )
        contains_future_information = bool(
            analysis.future_information.get("contains_future_information")
        )
        if contains_future_information:
            raise BatchResearchRecordingError(
                "LOCK_VALIDATION_TRIAL cannot lock a prediction result containing future information"
            )

        hypothesis = next(
            (
                item
                for item in package.predictive_hypotheses
                if item.hypothesis_id == hypothesis_id
            ),
            None,
        )
        if hypothesis is None:
            raise BatchResearchRecordingError(
                f"validation trial references unknown predictive hypothesis: {hypothesis_id}"
            )
        trial = PredictiveValidationTrialRecord(
            trial_id=trial_id,
            prediction_result_id=prediction_result_id,
            prediction_statement=prediction_statement,
            prediction_research_phase=analysis.research_phase,
            prediction_contains_future_information=False,
        )
        prior_trial = next(
            (
                item
                for item in hypothesis.trials
                if item.trial_id == trial_id
                or item.prediction_result_id == prediction_result_id
            ),
            None,
        )
        if prior_trial is not None:
            same_lock = (
                prior_trial.trial_id == trial.trial_id
                and prior_trial.prediction_result_id == trial.prediction_result_id
                and prior_trial.prediction_statement == trial.prediction_statement
                and prior_trial.prediction_research_phase == trial.prediction_research_phase
                and prior_trial.prediction_contains_future_information
                == trial.prediction_contains_future_information
            )
            if same_lock:
                return package
            raise BatchResearchRecordingError(
                "predictive validation trial identity already exists with different lock content"
            )
        return package.lock_predictive_validation_trial(
            hypothesis_id=hypothesis_id,
            trial=trial,
        )

    def _record_predictive_validation_outcome(
        self,
        package: ResearchPackage,
        update: Mapping[str, Any],
        *,
        current_result_ids: set[str],
    ) -> ResearchPackage:
        hypothesis_id = self._require_nonblank(update, "hypothesis_id")
        trial_id = self._require_nonblank(update, "trial_id")
        outcome_result_id = self._require_nonblank(update, "outcome_result_id")
        success = update.get("success")
        if not isinstance(success, bool):
            raise BatchResearchRecordingError(
                "RECORD_VALIDATION_OUTCOME requires boolean success"
            )
        if outcome_result_id not in current_result_ids:
            raise BatchResearchRecordingError(
                "RECORD_VALIDATION_OUTCOME outcome_result_id must come from the immediately completed batch"
            )
        outcome_matches = [
            item for item in package.analyses if item.result_id == outcome_result_id
        ]
        if len(outcome_matches) != 1:
            raise BatchResearchRecordingError(
                f"outcome result_id is not unique in RP: {outcome_result_id}"
            )
        outcome_analysis = outcome_matches[0]
        outcome_contains_future_information = bool(
            outcome_analysis.future_information.get("contains_future_information")
        )
        hypothesis = next(
            (
                item
                for item in package.predictive_hypotheses
                if item.hypothesis_id == hypothesis_id
            ),
            None,
        )
        if hypothesis is None:
            raise BatchResearchRecordingError(
                f"validation outcome references unknown predictive hypothesis: {hypothesis_id}"
            )
        trial = next((item for item in hypothesis.trials if item.trial_id == trial_id), None)
        if trial is None:
            raise BatchResearchRecordingError(
                f"validation outcome references unlocked trial: {trial_id}"
            )
        if trial.outcome_result_id is not None:
            same_outcome = (
                trial.outcome_result_id == outcome_result_id
                and trial.success == success
                and trial.outcome_contains_future_information
                == outcome_contains_future_information
            )
            if same_outcome:
                return package
            raise BatchResearchRecordingError(
                "predictive validation outcome already exists with different content"
            )
        return package.record_predictive_validation_outcome(
            hypothesis_id=hypothesis_id,
            trial_id=trial_id,
            outcome_result_id=outcome_result_id,
            success=success,
            outcome_contains_future_information=outcome_contains_future_information,
        )

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
