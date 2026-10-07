from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Mapping

from .research_package import (
    PredictiveHypothesisRecord,
    PredictiveValidationTrialRecord,
    ResearchPackageError,
)
from .validation_frontier import trial_id


class ProspectiveValidationError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_utc(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProspectiveValidationError(
            f"{field_name} must be an ISO-8601 timestamp: {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        raise ProspectiveValidationError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _nonblank(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProspectiveValidationError(f"{field_name} cannot be blank")
    return value.strip()


@dataclass(frozen=True, slots=True)
class ProspectiveValidationProtocol:
    """AI-authored scientific mechanics frozen before prospective outcomes exist.

    Deterministic code validates and executes this representation. It does not
    choose the data source, matching rule, eligibility rule, overlap rule, horizon,
    ordering, tie handling, or embargo policy.
    """

    protocol_id: str
    hypothesis_id: str
    source_subject_id: str
    route: str
    frozen_hypothesis_statement: str
    frozen_success_definition: str
    minimum_required_trials: int
    collection_start_utc: str
    last_historical_exposure_utc: str
    authoritative_daily_close_series: str
    exchange_session_calendar: str
    corporate_action_adjustment_policy: str
    missing_or_corrected_data_policy: str
    candidate_condition: str
    comparison_condition: str
    matching_rule: str
    observation_eligibility: str
    outcome_horizon_sessions: int
    non_overlap_scope: str
    tie_handling: str
    trial_ordering_rule: str
    outcome_embargo_rule: str
    outcome_evaluable_rule: str
    authored_by: str = "AI_RESEARCH_DIRECTOR"
    frozen_at_utc: str = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        for field_name in (
            "protocol_id",
            "hypothesis_id",
            "source_subject_id",
            "frozen_hypothesis_statement",
            "frozen_success_definition",
            "authoritative_daily_close_series",
            "exchange_session_calendar",
            "corporate_action_adjustment_policy",
            "missing_or_corrected_data_policy",
            "candidate_condition",
            "comparison_condition",
            "matching_rule",
            "observation_eligibility",
            "tie_handling",
            "trial_ordering_rule",
            "outcome_embargo_rule",
            "outcome_evaluable_rule",
            "authored_by",
        ):
            _nonblank(getattr(self, field_name), field_name)
        if self.route != "FUTURE_SAME_SUBJECT":
            raise ProspectiveValidationError(
                "prospective same-subject protocol requires route=FUTURE_SAME_SUBJECT"
            )
        if self.minimum_required_trials <= 0:
            raise ProspectiveValidationError("minimum_required_trials must be positive")
        if self.outcome_horizon_sessions <= 0:
            raise ProspectiveValidationError("outcome_horizon_sessions must be positive")
        if self.non_overlap_scope not in {"BETWEEN_TRIALS_ONLY", "ALL_OBSERVATIONS"}:
            raise ProspectiveValidationError(
                "non_overlap_scope must be BETWEEN_TRIALS_ONLY or ALL_OBSERVATIONS"
            )
        collection_start = _parse_utc(self.collection_start_utc, "collection_start_utc")
        exposure_cutoff = _parse_utc(
            self.last_historical_exposure_utc, "last_historical_exposure_utc"
        )
        _parse_utc(self.frozen_at_utc, "frozen_at_utc")
        if collection_start <= exposure_cutoff:
            raise ProspectiveValidationError(
                "collection_start_utc must be strictly after last_historical_exposure_utc"
            )

    def validate_against_hypothesis(self, hypothesis: PredictiveHypothesisRecord) -> None:
        if self.hypothesis_id != hypothesis.hypothesis_id:
            raise ProspectiveValidationError("protocol hypothesis_id changed")
        if self.frozen_hypothesis_statement != hypothesis.statement:
            raise ProspectiveValidationError("protocol changed frozen hypothesis statement")
        if self.frozen_success_definition != hypothesis.success_definition:
            raise ProspectiveValidationError("protocol changed frozen success definition")
        if self.minimum_required_trials != hypothesis.minimum_required_trials:
            raise ProspectiveValidationError("protocol changed minimum_required_trials")

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class ProspectiveTrialLock:
    trial_id: str
    ordinal: int
    prediction_result_id: str
    prediction_statement: str
    candidate_session_index: int
    comparison_session_index: int
    evaluable_after_session_index: int
    state: str = "LOCKED"
    outcome_result_id: str | None = None
    success: bool | None = None
    locked_at_utc: str = field(default_factory=_utc_now)
    completed_at_utc: str | None = None

    def __post_init__(self) -> None:
        if self.ordinal <= 0:
            raise ProspectiveValidationError("trial ordinal must be positive")
        _nonblank(self.trial_id, "trial_id")
        _nonblank(self.prediction_result_id, "prediction_result_id")
        _nonblank(self.prediction_statement, "prediction_statement")
        if self.candidate_session_index < 0 or self.comparison_session_index < 0:
            raise ProspectiveValidationError("session indexes cannot be negative")
        if self.evaluable_after_session_index < max(
            self.candidate_session_index, self.comparison_session_index
        ):
            raise ProspectiveValidationError(
                "evaluable_after_session_index cannot precede the matched observations"
            )
        if self.state not in {"LOCKED", "COMPLETED"}:
            raise ProspectiveValidationError(f"invalid prospective trial state: {self.state}")
        if self.state == "LOCKED" and (
            self.outcome_result_id is not None
            or self.success is not None
            or self.completed_at_utc is not None
        ):
            raise ProspectiveValidationError("LOCKED trial cannot already contain an outcome")
        if self.state == "COMPLETED" and (
            self.outcome_result_id is None
            or self.success is None
            or self.completed_at_utc is None
        ):
            raise ProspectiveValidationError("COMPLETED trial requires outcome fields")


@dataclass(frozen=True, slots=True)
class ProspectiveValidationFrontier:
    protocol_id: str
    protocol_fingerprint: str
    hypothesis_id: str
    source_subject_id: str
    required_trials: int
    outcome_horizon_sessions: int
    non_overlap_scope: str
    state: str = "ARMED"
    trials: tuple[ProspectiveTrialLock, ...] = ()

    def __post_init__(self) -> None:
        if self.required_trials <= 0 or self.outcome_horizon_sessions <= 0:
            raise ProspectiveValidationError("frontier trial count/horizon must be positive")
        if self.state not in {"ARMED", "IN_PROGRESS", "COMPLETE"}:
            raise ProspectiveValidationError(f"invalid prospective frontier state: {self.state}")
        if len(self.trials) > self.required_trials:
            raise ProspectiveValidationError("frontier contains more trials than protocol permits")

    @classmethod
    def arm(cls, protocol: ProspectiveValidationProtocol) -> "ProspectiveValidationFrontier":
        return cls(
            protocol_id=protocol.protocol_id,
            protocol_fingerprint=protocol.fingerprint,
            hypothesis_id=protocol.hypothesis_id,
            source_subject_id=protocol.source_subject_id,
            required_trials=protocol.minimum_required_trials,
            outcome_horizon_sessions=protocol.outcome_horizon_sessions,
            non_overlap_scope=protocol.non_overlap_scope,
        )

    @property
    def next_ordinal(self) -> int:
        return len(self.trials) + 1

    @staticmethod
    def _window(index: int, horizon: int) -> tuple[int, int]:
        return (index + 1, index + horizon)

    @staticmethod
    def _overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
        return left[0] <= right[1] and right[0] <= left[1]

    def _require_nonoverlap(self, candidate_index: int, comparison_index: int) -> None:
        new_windows = (
            self._window(candidate_index, self.outcome_horizon_sessions),
            self._window(comparison_index, self.outcome_horizon_sessions),
        )
        if self.non_overlap_scope == "ALL_OBSERVATIONS" and self._overlap(
            new_windows[0], new_windows[1]
        ):
            raise ProspectiveValidationError(
                "candidate/comparison outcome windows overlap under ALL_OBSERVATIONS protocol"
            )
        for existing in self.trials:
            old_windows = (
                self._window(existing.candidate_session_index, self.outcome_horizon_sessions),
                self._window(existing.comparison_session_index, self.outcome_horizon_sessions),
            )
            if any(self._overlap(new, old) for new in new_windows for old in old_windows):
                raise ProspectiveValidationError(
                    f"trial outcome windows overlap prior trial {existing.trial_id}"
                )

    def lock_trial(
        self,
        *,
        prediction_result_id: str,
        prediction_statement: str,
        candidate_session_index: int,
        comparison_session_index: int,
        prediction_contains_future_information: bool,
        hypothesis: PredictiveHypothesisRecord,
    ) -> tuple["ProspectiveValidationFrontier", PredictiveHypothesisRecord]:
        if self.state == "COMPLETE":
            raise ProspectiveValidationError("validation frontier is complete")
        if prediction_contains_future_information:
            raise ProspectiveValidationError("prospective prediction cannot contain future information")
        if hypothesis.hypothesis_id != self.hypothesis_id:
            raise ProspectiveValidationError("frontier/hypothesis identity mismatch")
        if len(hypothesis.trials) != len(self.trials):
            raise ProspectiveValidationError("frontier and hypothesis trial counts diverged")
        if self.next_ordinal > self.required_trials:
            raise ProspectiveValidationError("protocol trial limit reached")
        self._require_nonoverlap(candidate_session_index, comparison_session_index)
        expected_trial_id = trial_id(self.hypothesis_id, self.next_ordinal)
        evaluable_after = max(candidate_session_index, comparison_session_index) + self.outcome_horizon_sessions
        lock = ProspectiveTrialLock(
            trial_id=expected_trial_id,
            ordinal=self.next_ordinal,
            prediction_result_id=_nonblank(prediction_result_id, "prediction_result_id"),
            prediction_statement=_nonblank(prediction_statement, "prediction_statement"),
            candidate_session_index=candidate_session_index,
            comparison_session_index=comparison_session_index,
            evaluable_after_session_index=evaluable_after,
        )
        hypothesis_trial = PredictiveValidationTrialRecord(
            trial_id=expected_trial_id,
            prediction_result_id=lock.prediction_result_id,
            prediction_statement=lock.prediction_statement,
            prediction_research_phase="VALIDATION",
            prediction_contains_future_information=False,
        )
        try:
            updated_hypothesis = hypothesis.lock_validation_trial(hypothesis_trial)
        except ResearchPackageError as exc:
            raise ProspectiveValidationError(str(exc)) from exc
        updated = replace(
            self,
            trials=self.trials + (lock,),
            state="IN_PROGRESS",
        )
        return updated, updated_hypothesis

    def record_outcome(
        self,
        *,
        trial_id_value: str,
        outcome_result_id: str,
        success: bool,
        current_session_index: int,
        hypothesis: PredictiveHypothesisRecord,
    ) -> tuple["ProspectiveValidationFrontier", PredictiveHypothesisRecord]:
        matches = [i for i, item in enumerate(self.trials) if item.trial_id == trial_id_value]
        if len(matches) != 1:
            raise ProspectiveValidationError(
                f"outcome requires exactly one frontier trial match: {trial_id_value}"
            )
        index = matches[0]
        locked = self.trials[index]
        if locked.state != "LOCKED":
            raise ProspectiveValidationError(f"trial outcome already recorded: {trial_id_value}")
        if current_session_index < locked.evaluable_after_session_index:
            raise ProspectiveValidationError(
                "outcome embargo active: terminal return is not yet evaluable"
            )
        try:
            updated_hypothesis = hypothesis.record_validation_outcome(
                trial_id=trial_id_value,
                outcome_result_id=_nonblank(outcome_result_id, "outcome_result_id"),
                success=success,
                outcome_contains_future_information=True,
            )
        except ResearchPackageError as exc:
            raise ProspectiveValidationError(str(exc)) from exc
        completed = replace(
            locked,
            state="COMPLETED",
            outcome_result_id=outcome_result_id,
            success=success,
            completed_at_utc=_utc_now(),
        )
        trials = list(self.trials)
        trials[index] = completed
        completed_count = sum(1 for item in trials if item.state == "COMPLETED")
        state = "COMPLETE" if completed_count == self.required_trials else "IN_PROGRESS"
        return replace(self, trials=tuple(trials), state=state), updated_hypothesis


class JsonProspectiveValidationStore:
    FORMAT = "MTS_V4_PROSPECTIVE_VALIDATION_V1"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(
        self,
        *,
        protocol: ProspectiveValidationProtocol,
        frontier: ProspectiveValidationFrontier,
    ) -> None:
        if frontier.protocol_fingerprint != protocol.fingerprint:
            raise ProspectiveValidationError("frontier protocol fingerprint mismatch")
        document = {
            "format": self.FORMAT,
            "protocol": asdict(protocol),
            "frontier": asdict(frontier),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def load(self) -> tuple[ProspectiveValidationProtocol, ProspectiveValidationFrontier]:
        if not self.path.exists():
            raise ProspectiveValidationError(f"prospective validation state does not exist: {self.path}")
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if raw.get("format") != self.FORMAT:
            raise ProspectiveValidationError("unsupported prospective validation format")
        protocol = ProspectiveValidationProtocol(**raw["protocol"])
        raw_frontier = dict(raw["frontier"])
        raw_frontier["trials"] = tuple(
            ProspectiveTrialLock(**item) for item in raw_frontier.get("trials", ())
        )
        frontier = ProspectiveValidationFrontier(**raw_frontier)
        if frontier.protocol_fingerprint != protocol.fingerprint:
            raise ProspectiveValidationError("stored frontier protocol fingerprint mismatch")
        return protocol, frontier
