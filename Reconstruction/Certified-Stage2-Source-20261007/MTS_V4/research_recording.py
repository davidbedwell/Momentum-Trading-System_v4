from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from .contracts import AnalysisRequest, ResearchDecision, SubjectMetadata
from .decision_journal import JsonResearchDecisionJournal
from .research_package import (
    PredictiveHypothesisRecord,
    PredictiveValidationTrialRecord,
    ResearchAnalysisRecord,
    ResearchPackage,
    ResearchQuestionRecord,
)
from .research_package_store import JsonResearchPackageStore


class ResearchRecordingError(RuntimeError):
    pass


class CampaignResearchRecorder:
    """Mechanical persistence of AI-authored research structure.

    RD chooses RP identity, question lineage, scientific interpretation,
    hypotheses, trial predictions, trial success judgments, findings, and
    closure. This recorder validates only durable identity, lineage,
    frozen-hypothesis integrity, and the human-approved verification rule.
    """

    def __init__(
        self,
        *,
        package_store: JsonResearchPackageStore,
        decision_journal: JsonResearchDecisionJournal,
    ) -> None:
        self._packages = package_store
        self._journal = decision_journal

    def record_decision(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        decision: ResearchDecision,
        decision_sequence: int,
        analyses_executed: int,
    ) -> None:
        self._journal.append(
            campaign_id=campaign_id,
            decision_sequence=decision_sequence,
            analyses_executed=analyses_executed,
            decision=decision,
        )

        if decision.interpreted_request_id is not None:
            self._record_interpretation(decision)

        self._record_predictive_hypothesis_updates(decision)
        self._record_findings(decision)

        if not decision.continue_research:
            self._record_closure(decision)

    def record_accepted_request(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
    ) -> None:
        """Persist only an Analysis request that passed objective validation."""
        self._record_request(
            campaign_id=campaign_id,
            subject=subject,
            request=request,
        )

    def _record_request(
        self,
        *,
        campaign_id: str,
        subject: SubjectMetadata,
        request: AnalysisRequest,
    ) -> None:
        if not request.rp_id or not request.question_id:
            raise ResearchRecordingError(
                "live RD Analysis request is missing rp_id/question_id lineage"
            )
        if request.subject_id != subject.subject_id:
            raise ResearchRecordingError("RP request subject does not match active subject")

        package = self._packages.load(request.rp_id)
        created = package is None
        if package is None:
            package = ResearchPackage(
                rp_id=request.rp_id,
                subject_id=subject.subject_id,
                campaign_id=campaign_id,
                parent_rp_id=request.parent_rp_id,
                originating_question=request.question,
                originating_rationale=request.rationale,
            )
            self._packages.create(package)
        elif package.campaign_id != campaign_id:
            raise ResearchRecordingError(
                f"research package belongs to another campaign: {request.rp_id}"
            )

        changed = False
        if not any(item.question_id == request.question_id for item in package.questions):
            package = package.append_question(
                ResearchQuestionRecord(
                    question_id=request.question_id,
                    parent_question_id=request.parent_question_id,
                    question=request.question,
                    rationale=request.rationale,
                    research_phase=request.research_phase.value,
                )
            )
            changed = True

        if not any(item.request_id == request.request_id for item in package.analyses):
            package = package.append_analysis(
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
            changed = True

        if changed:
            self._packages.save(package)
        elif created:
            raise ResearchRecordingError("new RP was created without durable request lineage")

    def _record_interpretation(self, decision: ResearchDecision) -> None:
        if decision.interpreted_result_id is None:
            raise ResearchRecordingError(
                "interpreted_request_id requires interpreted_result_id"
            )
        match: ResearchPackage | None = None
        for rp_id in self._packages.list_ids():
            candidate = self._packages.load(rp_id)
            if candidate is None:
                continue
            if any(
                item.request_id == decision.interpreted_request_id
                for item in candidate.analyses
            ):
                if match is not None:
                    raise ResearchRecordingError(
                        f"interpreted request appears in multiple RPs: {decision.interpreted_request_id}"
                    )
                match = candidate
        if match is None:
            raise ResearchRecordingError(
                f"interpreted request is not present in a durable RP: {decision.interpreted_request_id}"
            )
        existing = next(
            item
            for item in match.analyses
            if item.request_id == decision.interpreted_request_id
        )
        future_information = dict(decision.interpreted_future_information)
        if (
            existing.result_id == decision.interpreted_result_id
            and existing.execution_status == decision.interpreted_execution_status
            and existing.interpretation == decision.analysis_interpretation
            and dict(existing.future_information) == future_information
        ):
            return
        evolved = match.record_analysis_outcome(
            request_id=decision.interpreted_request_id,
            result_id=decision.interpreted_result_id,
            execution_status=decision.interpreted_execution_status,
            interpretation=decision.analysis_interpretation,
            future_information=future_information,
        )
        self._packages.save(evolved)

    @staticmethod
    def _require_nonblank(update: Mapping[str, Any], key: str) -> str:
        value = update.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ResearchRecordingError(f"predictive hypothesis update requires nonblank {key}")
        return value

    def _record_predictive_hypothesis_updates(self, decision: ResearchDecision) -> None:
        raw_updates = decision.research_state.get("predictive_hypothesis_updates", [])
        if raw_updates in (None, []):
            return
        if not isinstance(raw_updates, list):
            raise ResearchRecordingError(
                "research_state.predictive_hypothesis_updates must be a list"
            )
        if not decision.rp_id:
            raise ResearchRecordingError("predictive hypothesis updates require decision.rp_id")
        package = self._packages.load(decision.rp_id)
        if package is None:
            raise ResearchRecordingError(
                f"predictive hypothesis update references unknown RP: {decision.rp_id}"
            )

        evolved = package
        for raw in raw_updates:
            if not isinstance(raw, Mapping):
                raise ResearchRecordingError("each predictive hypothesis update must be an object")
            action = raw.get("action")
            if action == "CREATE_TENTATIVE":
                evolved = self._create_tentative_predictive_hypothesis(evolved, raw)
            elif action == "LOCK_VALIDATION_TRIAL":
                evolved = self._lock_predictive_validation_trial(
                    evolved,
                    raw,
                    decision=decision,
                )
            elif action == "RECORD_VALIDATION_OUTCOME":
                evolved = self._record_predictive_validation_outcome(
                    evolved,
                    raw,
                    decision=decision,
                )
            else:
                raise ResearchRecordingError(
                    f"unknown predictive hypothesis update action: {action!r}"
                )

        if evolved is not package:
            self._packages.save(evolved)

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
            raise ResearchRecordingError(
                "CREATE_TENTATIVE requires positive integer minimum_required_trials"
            )
        source_result_ids = update.get("source_result_ids")
        if (
            not isinstance(source_result_ids, list)
            or not source_result_ids
            or not all(isinstance(value, str) and value.strip() for value in source_result_ids)
        ):
            raise ResearchRecordingError(
                "CREATE_TENTATIVE requires nonempty source_result_ids list"
            )

        source_analyses = []
        for result_id in source_result_ids:
            matches = [item for item in package.analyses if item.result_id == result_id]
            if len(matches) != 1:
                raise ResearchRecordingError(
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
            raise ResearchRecordingError(
                f"predictive hypothesis definition is frozen; use a new hypothesis_id: {hypothesis_id}"
            )

        hypothesis = PredictiveHypothesisRecord(
            hypothesis_id=hypothesis_id,
            statement=statement,
            success_definition=success_definition,
            minimum_required_trials=minimum_required_trials,
            source_result_ids=tuple(source_result_ids),
            discovered_with_lookahead=discovered_with_lookahead,
        )
        return package.append_predictive_hypothesis(hypothesis)

    def _lock_predictive_validation_trial(
        self,
        package: ResearchPackage,
        update: Mapping[str, Any],
        *,
        decision: ResearchDecision,
    ) -> ResearchPackage:
        hypothesis_id = self._require_nonblank(update, "hypothesis_id")
        trial_id = self._require_nonblank(update, "trial_id")
        prediction_result_id = self._require_nonblank(update, "prediction_result_id")
        prediction_statement = self._require_nonblank(update, "prediction_statement")
        if decision.interpreted_result_id != prediction_result_id:
            raise ResearchRecordingError(
                "prediction_result_id must equal the currently interpreted result_id"
            )

        matches = [item for item in package.analyses if item.result_id == prediction_result_id]
        if len(matches) != 1:
            raise ResearchRecordingError(
                f"prediction result_id is not unique in RP: {prediction_result_id}"
            )
        analysis = matches[0]
        contains_future_information = bool(
            analysis.future_information.get("contains_future_information")
        )
        trial = PredictiveValidationTrialRecord(
            trial_id=trial_id,
            prediction_result_id=prediction_result_id,
            prediction_statement=prediction_statement,
            prediction_research_phase=analysis.research_phase,
            prediction_contains_future_information=contains_future_information,
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
            raise ResearchRecordingError(
                f"validation trial references unknown predictive hypothesis: {hypothesis_id}"
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
            raise ResearchRecordingError(
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
        decision: ResearchDecision,
    ) -> ResearchPackage:
        hypothesis_id = self._require_nonblank(update, "hypothesis_id")
        trial_id = self._require_nonblank(update, "trial_id")
        outcome_result_id = self._require_nonblank(update, "outcome_result_id")
        success = update.get("success")
        if not isinstance(success, bool):
            raise ResearchRecordingError(
                "RECORD_VALIDATION_OUTCOME requires boolean success"
            )
        if decision.interpreted_result_id != outcome_result_id:
            raise ResearchRecordingError(
                "outcome_result_id must equal the currently interpreted result_id"
            )

        outcome_matches = [
            item for item in package.analyses if item.result_id == outcome_result_id
        ]
        if len(outcome_matches) != 1:
            raise ResearchRecordingError(
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
            raise ResearchRecordingError(
                f"validation outcome references unknown predictive hypothesis: {hypothesis_id}"
            )
        trial = next(
            (item for item in hypothesis.trials if item.trial_id == trial_id),
            None,
        )
        if trial is None:
            raise ResearchRecordingError(
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
            raise ResearchRecordingError(
                "predictive validation outcome already exists with different content"
            )

        return package.record_predictive_validation_outcome(
            hypothesis_id=hypothesis_id,
            trial_id=trial_id,
            outcome_result_id=outcome_result_id,
            success=success,
            outcome_contains_future_information=outcome_contains_future_information,
        )

    def _record_findings(self, decision: ResearchDecision) -> None:
        if not decision.promote_findings:
            return
        if not decision.rp_id:
            raise ResearchRecordingError("promoted findings require decision.rp_id")
        package = self._packages.load(decision.rp_id)
        if package is None:
            raise ResearchRecordingError(
                f"finding references unknown research package: {decision.rp_id}"
            )
        existing_ids = {
            str(item.get("finding_id"))
            for item in package.findings
            if isinstance(item, Mapping)
        }
        evolved = package
        for finding in decision.promote_findings:
            if finding.finding_id in existing_ids:
                continue
            evolved = evolved.append_finding(asdict(finding))
            existing_ids.add(finding.finding_id)
        if evolved is not package:
            self._packages.save(evolved)

    def _record_closure(self, decision: ResearchDecision) -> None:
        if not decision.rp_id:
            raise ResearchRecordingError("scientific closure requires decision.rp_id")
        package = self._packages.load(decision.rp_id)
        if package is None:
            raise ResearchRecordingError(
                f"scientific closure references unknown research package: {decision.rp_id}"
            )
        if package.status == "CLOSED":
            return
        close_reason = (decision.close_reason or "AI_RD_SCIENTIFIC_CLOSURE").strip()
        final_assessment = decision.analysis_interpretation
        self._packages.save(
            package.close(
                close_reason=close_reason,
                final_assessment=final_assessment,
            )
        )