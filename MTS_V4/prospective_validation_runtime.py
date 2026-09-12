from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

from .prospective_validation import (
    JsonProspectiveValidationStore,
    ProspectiveValidationError,
    ProspectiveValidationFrontier,
    ProspectiveValidationProtocol,
)
from .research_package import PredictiveHypothesisRecord, ResearchPackage
from .research_package_store import JsonResearchPackageStore


getcontext().prec = 50
_NEW_YORK = ZoneInfo("America/New_York")


@dataclass(frozen=True, slots=True)
class ProspectiveExecutionPlan:
    """Mechanical representation of one already-authored frozen protocol.

    Values here are not scientific defaults. They are compiled only when the
    frozen protocol text admits one unambiguous semantics-preserving reading.
    """

    protocol_fingerprint: str
    sma_window_sessions: int
    match_search_sessions: int
    outcome_horizon_sessions: int
    terminal_finalization_lag_sessions: int
    condition_threshold: Decimal
    collective_embargo: bool


@dataclass(frozen=True, slots=True)
class AuthoritativeSession:
    """One official XNAS session supplied by the validation-data custodian.

    ``mandatory_share_multiplier`` is the exact mandatory share-count
    multiplier effective on this session. Use 1 when no such action is effective.
    A row with ``nocp=None`` still represents an official XNAS session and
    therefore still occupies a calendar position.
    """

    session_index: int
    session_date: str
    source_subject_id: str
    source_identity: str
    nocp: str | None
    mandatory_share_multiplier: str | None

    def __post_init__(self) -> None:
        if self.session_index < 0:
            raise ProspectiveValidationError("session_index cannot be negative")
        try:
            datetime.fromisoformat(self.session_date)
        except ValueError as exc:
            raise ProspectiveValidationError(
                f"session_date must be ISO date: {self.session_date!r}"
            ) from exc
        if self.source_identity != "NASDAQ_NOCP":
            raise ProspectiveValidationError(
                "prospective validation requires source_identity=NASDAQ_NOCP"
            )
        if self.nocp is not None:
            value = Decimal(self.nocp)
            if value <= 0:
                raise ProspectiveValidationError("NOCP must be positive")
        if self.mandatory_share_multiplier is not None:
            factor = Decimal(self.mandatory_share_multiplier)
            if factor <= 0:
                raise ProspectiveValidationError(
                    "mandatory_share_multiplier must be positive"
                )


@dataclass(frozen=True, slots=True)
class PublicConditionObservation:
    session_index: int
    session_date: str
    eligible: bool
    condition: str | None
    input_freeze_utc: str | None
    observation_commitment: str


@dataclass(frozen=True, slots=True)
class MatchedPair:
    candidate: PublicConditionObservation
    comparison: PublicConditionObservation


@dataclass(frozen=True, slots=True)
class RuntimeAdvanceResult:
    processed_conditions: int
    newly_locked_trials: tuple[str, ...]
    next_trial_id: str | None
    frontier_state: str
    gate_closed_through_session_index: int | None


def _single_int(pattern: str, text: str, field_name: str) -> int:
    values = {int(value) for value in re.findall(pattern, text, flags=re.IGNORECASE)}
    if len(values) != 1:
        raise ProspectiveValidationError(
            f"cannot unambiguously compile {field_name} from frozen protocol"
        )
    return next(iter(values))


def compile_execution_plan(protocol: ProspectiveValidationProtocol) -> ProspectiveExecutionPlan:
    """Compile objective execution quantities already fixed by the protocol.

    This function deliberately refuses ambiguity rather than inventing science.
    """

    sma_window = _single_int(
        r"(?:SMA20|20-session|20 required close records|preceding 19 XNAS sessions)",
        "20" if "SMA20" in protocol.authoritative_daily_close_series else "",
        "SMA window",
    )
    if sma_window != 20:
        raise ProspectiveValidationError("compiled SMA window is inconsistent")

    search_sessions = _single_int(
        r"next\s+(\d+)\s+Nasdaq sessions",
        protocol.matching_rule,
        "matching search window",
    )
    finalization_lag = _single_int(
        r"fifth\s+Nasdaq session after the terminal session",
        protocol.missing_or_corrected_data_policy,
        "terminal finalization lag",
    ) if "fifth Nasdaq session after the terminal session" in protocol.missing_or_corrected_data_policy else 0
    if finalization_lag == 0:
        raise ProspectiveValidationError(
            "cannot unambiguously compile terminal finalization lag from frozen protocol"
        )
    # The authored word 'fifth' has one exact numerical representation.
    finalization_lag = 5

    if "greater than or equal to zero" not in protocol.candidate_condition.lower():
        raise ProspectiveValidationError("candidate zero threshold is not uniquely represented")
    if "less than zero" not in protocol.comparison_condition.lower():
        raise ProspectiveValidationError("comparison zero threshold is not uniquely represented")
    if "No validation outcome may be decrypted" not in protocol.outcome_embargo_rule:
        raise ProspectiveValidationError("collective embargo is not uniquely represented")

    return ProspectiveExecutionPlan(
        protocol_fingerprint=protocol.fingerprint,
        sma_window_sessions=20,
        match_search_sessions=search_sessions,
        outcome_horizon_sessions=protocol.outcome_horizon_sessions,
        terminal_finalization_lag_sessions=finalization_lag,
        condition_threshold=Decimal("0"),
        collective_embargo=True,
    )


def _freeze_time_utc(next_session_date: str) -> str:
    local = datetime.fromisoformat(next_session_date).replace(
        hour=9, minute=0, second=0, microsecond=0, tzinfo=_NEW_YORK
    )
    return local.astimezone(ZoneInfo("UTC")).isoformat()


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ProspectiveValidationError("as_of_utc must include a timezone")
    return parsed.astimezone(ZoneInfo("UTC"))


def _validate_session_series(
    sessions: Sequence[AuthoritativeSession], *, source_subject_id: str
) -> None:
    if not sessions:
        raise ProspectiveValidationError("authoritative session series is empty")
    prior_index: int | None = None
    prior_date: str | None = None
    seen: set[int] = set()
    for row in sessions:
        if row.source_subject_id != source_subject_id:
            raise ProspectiveValidationError("authoritative session subject mismatch")
        if row.session_index in seen:
            raise ProspectiveValidationError(
                f"duplicate session_index: {row.session_index}"
            )
        seen.add(row.session_index)
        if prior_index is not None and row.session_index != prior_index + 1:
            raise ProspectiveValidationError(
                "authoritative series must contain every consecutive XNAS session"
            )
        if prior_date is not None and row.session_date <= prior_date:
            raise ProspectiveValidationError(
                "authoritative session dates must be strictly increasing"
            )
        prior_index = row.session_index
        prior_date = row.session_date


def build_public_condition_feed(
    *,
    protocol: ProspectiveValidationProtocol,
    sessions: Sequence[AuthoritativeSession],
    as_of_utc: str,
) -> tuple[PublicConditionObservation, ...]:
    """Convert official close history into outcome-free condition labels.

    Raw closes and returns do not leave this custodian boundary. The matching
    runtime receives only eligibility, condition labels, dates, and commitments.
    """

    plan = compile_execution_plan(protocol)
    rows = tuple(sessions)
    _validate_session_series(rows, source_subject_id=protocol.source_subject_id)
    as_of = _parse_utc(as_of_utc)
    collection_start = _parse_utc(protocol.collection_start_utc)

    cumulative: list[Decimal | None] = []
    running = Decimal("1")
    for row in rows:
        factor = (
            Decimal(row.mandatory_share_multiplier)
            if row.mandatory_share_multiplier is not None
            else None
        )
        if factor is None:
            cumulative.append(None)
        else:
            running *= factor
            cumulative.append(running)

    public: list[PublicConditionObservation] = []
    for pos, row in enumerate(rows):
        if pos + 1 >= len(rows):
            break
        freeze_utc = _freeze_time_utc(rows[pos + 1].session_date)
        freeze_dt = _parse_utc(freeze_utc)
        close_time_local = datetime.fromisoformat(row.session_date).replace(
            hour=16, minute=0, second=0, microsecond=0, tzinfo=_NEW_YORK
        )
        close_time_utc = close_time_local.astimezone(ZoneInfo("UTC"))
        if close_time_utc <= collection_start or as_of < freeze_dt:
            continue

        start = pos - (plan.sma_window_sessions - 1)
        eligible = start >= 0
        window = rows[start : pos + 1] if eligible else ()
        if eligible:
            eligible = all(
                item.nocp is not None
                and item.mandatory_share_multiplier is not None
                for item in window
            )
        condition: str | None = None
        metric_text = "INELIGIBLE"
        if eligible:
            current_basis = cumulative[pos]
            if current_basis is None:
                eligible = False
            else:
                adjusted: list[Decimal] = []
                for offset, item in enumerate(window, start=start):
                    historical_basis = cumulative[offset]
                    if historical_basis is None or item.nocp is None:
                        eligible = False
                        adjusted = []
                        break
                    multiplier_after = current_basis / historical_basis
                    adjusted.append(Decimal(item.nocp) / multiplier_after)
                if eligible:
                    sma = sum(adjusted, Decimal("0")) / Decimal(
                        plan.sma_window_sessions
                    )
                    current = Decimal(row.nocp or "0")
                    metric = current / sma - Decimal("1")
                    condition = "CANDIDATE" if metric >= plan.condition_threshold else "COMPARISON"
                    metric_text = format(metric, "f")

        commitment_payload = {
            "protocol_fingerprint": protocol.fingerprint,
            "session_index": row.session_index,
            "session_date": row.session_date,
            "eligible": eligible,
            "condition": condition,
            "metric": metric_text,
            "freeze_utc": freeze_utc,
        }
        commitment = hashlib.sha256(
            json.dumps(commitment_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        public.append(
            PublicConditionObservation(
                session_index=row.session_index,
                session_date=row.session_date,
                eligible=eligible,
                condition=condition,
                input_freeze_utc=freeze_utc,
                observation_commitment=commitment,
            )
        )
    return tuple(public)


def _baseline_windows_overlap(
    left_index: int, right_index: int, horizon: int
) -> bool:
    left = (left_index, left_index + horizon)
    right = (right_index, right_index + horizon)
    return left[0] <= right[1] and right[0] <= left[1]


def _pair_overlaps_frontier(
    pair: MatchedPair,
    frontier: ProspectiveValidationFrontier,
    horizon: int,
) -> bool:
    new_indexes = (pair.candidate.session_index, pair.comparison.session_index)
    for prior in frontier.trials:
        old_indexes = (
            prior.candidate_session_index,
            prior.comparison_session_index,
        )
        if any(
            _baseline_windows_overlap(new, old, horizon)
            for new in new_indexes
            for old in old_indexes
        ):
            return True
    return False


def _existing_lock_key(frontier: ProspectiveValidationFrontier, ordinal: int) -> tuple[int, int] | None:
    if ordinal < 1 or ordinal > len(frontier.trials):
        return None
    item = frontier.trials[ordinal - 1]
    return (item.candidate_session_index, item.comparison_session_index)


def derive_pairs(
    *,
    protocol: ProspectiveValidationProtocol,
    conditions: Sequence[PublicConditionObservation],
    frontier: ProspectiveValidationFrontier,
) -> tuple[MatchedPair, ...]:
    """Apply the frozen serial matching rule without outcome access."""

    plan = compile_execution_plan(protocol)
    rows = tuple(sorted(conditions, key=lambda item: item.session_index))
    pairs: list[MatchedPair] = []
    pos = 0
    gate_closed_through = -1

    while pos < len(rows) and len(pairs) < protocol.minimum_required_trials:
        row = rows[pos]
        if row.session_index <= gate_closed_through or not row.eligible:
            pos += 1
            continue
        anchor = row
        match: PublicConditionObservation | None = None
        last_examined_pos = pos
        for j in range(pos + 1, len(rows)):
            candidate = rows[j]
            distance = candidate.session_index - anchor.session_index
            if distance > plan.match_search_sessions:
                break
            last_examined_pos = j
            if (
                candidate.eligible
                and candidate.condition is not None
                and candidate.condition != anchor.condition
            ):
                match = candidate
                break
        if match is None:
            if not rows or rows[-1].session_index < anchor.session_index + plan.match_search_sessions:
                break
            pos = last_examined_pos + 1
            while pos < len(rows) and rows[pos].session_index < anchor.session_index + plan.match_search_sessions + 1:
                pos += 1
            continue

        if anchor.condition == "CANDIDATE":
            pair = MatchedPair(candidate=anchor, comparison=match)
        else:
            pair = MatchedPair(candidate=match, comparison=anchor)
        if _pair_overlaps_frontier(pair, frontier, plan.outcome_horizon_sessions):
            raise ProspectiveValidationError(
                "deterministic pair reconstruction conflicts with persisted frontier overlap"
            )
        pairs.append(pair)
        gate_closed_through = max(
            pair.candidate.session_index,
            pair.comparison.session_index,
        ) + plan.outcome_horizon_sessions
        pos = j + 1
        while pos < len(rows) and rows[pos].session_index <= gate_closed_through:
            pos += 1
    return tuple(pairs)


def _find_hypothesis(package: ResearchPackage, hypothesis_id: str) -> PredictiveHypothesisRecord:
    matches = [
        item for item in package.predictive_hypotheses if item.hypothesis_id == hypothesis_id
    ]
    if len(matches) != 1:
        raise ProspectiveValidationError(
            f"expected exactly one predictive hypothesis {hypothesis_id}"
        )
    return matches[0]


def advance_matching_runtime(
    *,
    protocol_store: JsonProspectiveValidationStore,
    research_package_store: JsonResearchPackageStore,
    rp_id: str,
    conditions: Sequence[PublicConditionObservation],
) -> RuntimeAdvanceResult:
    """Lock any newly available trials while preserving collective outcome embargo."""

    protocol, frontier = protocol_store.load()
    package = research_package_store.load(rp_id)
    if package is None:
        raise ProspectiveValidationError(f"research package does not exist: {rp_id}")
    hypothesis = _find_hypothesis(package, protocol.hypothesis_id)
    protocol.validate_against_hypothesis(hypothesis)

    derived = derive_pairs(protocol=protocol, conditions=conditions, frontier=ProspectiveValidationFrontier.arm(protocol))
    newly_locked: list[str] = []

    for ordinal, pair in enumerate(derived, 1):
        persisted_key = _existing_lock_key(frontier, ordinal)
        pair_key = (pair.candidate.session_index, pair.comparison.session_index)
        if persisted_key is not None:
            if persisted_key != pair_key:
                raise ProspectiveValidationError(
                    f"persisted trial {ordinal} disagrees with deterministic reconstruction"
                )
            continue
        if frontier.next_ordinal != ordinal:
            raise ProspectiveValidationError("frontier trial sequence is not contiguous")
        if frontier.next_ordinal > frontier.required_trials:
            break
        trial_name = f"{protocol.hypothesis_id}-T{ordinal:02d}"
        prediction_result_id = "prospective-lock:" + hashlib.sha256(
            (
                protocol.fingerprint
                + "|"
                + trial_name
                + "|"
                + pair.candidate.observation_commitment
                + "|"
                + pair.comparison.observation_commitment
            ).encode()
        ).hexdigest()
        statement = (
            f"{protocol.frozen_hypothesis_statement} "
            f"Locked trial {trial_name}: candidate session {pair.candidate.session_date}; "
            f"comparison session {pair.comparison.session_date}."
        )
        frontier, updated_hypothesis = frontier.lock_trial(
            prediction_result_id=prediction_result_id,
            prediction_statement=statement,
            candidate_session_index=pair.candidate.session_index,
            comparison_session_index=pair.comparison.session_index,
            prediction_contains_future_information=False,
            hypothesis=hypothesis,
        )
        hypotheses = list(package.predictive_hypotheses)
        index = next(
            i for i, item in enumerate(hypotheses) if item.hypothesis_id == hypothesis.hypothesis_id
        )
        hypotheses[index] = updated_hypothesis
        package = package._evolve(predictive_hypotheses=tuple(hypotheses))
        hypothesis = updated_hypothesis
        newly_locked.append(trial_name)

    if newly_locked:
        research_package_store.save(package)
        protocol_store.save(protocol=protocol, frontier=frontier)

    next_id = None
    if frontier.next_ordinal <= frontier.required_trials:
        next_id = f"{protocol.hypothesis_id}-T{frontier.next_ordinal:02d}"
    gate = None
    if frontier.trials:
        latest = frontier.trials[-1]
        gate = max(
            latest.candidate_session_index, latest.comparison_session_index
        ) + protocol.outcome_horizon_sessions
    return RuntimeAdvanceResult(
        processed_conditions=len(conditions),
        newly_locked_trials=tuple(newly_locked),
        next_trial_id=next_id,
        frontier_state=frontier.state,
        gate_closed_through_session_index=gate,
    )


def load_authoritative_sessions(path: str | Path) -> tuple[AuthoritativeSession, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping) or not isinstance(raw.get("sessions"), list):
        raise ProspectiveValidationError(
            "authoritative snapshot must be an object containing a sessions list"
        )
    return tuple(AuthoritativeSession(**dict(item)) for item in raw["sessions"])


def save_public_condition_feed(
    path: str | Path,
    *,
    protocol: ProspectiveValidationProtocol,
    as_of_utc: str,
    conditions: Iterable[PublicConditionObservation],
) -> None:
    document = {
        "format": "MTS_V4_PROSPECTIVE_PUBLIC_CONDITION_FEED_V1",
        "protocol_id": protocol.protocol_id,
        "protocol_fingerprint": protocol.fingerprint,
        "as_of_utc": as_of_utc,
        "contains_raw_prices": False,
        "contains_outcomes": False,
        "conditions": [asdict(item) for item in conditions],
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)


def load_public_condition_feed(
    path: str | Path,
    *,
    protocol: ProspectiveValidationProtocol,
) -> tuple[PublicConditionObservation, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("format") != "MTS_V4_PROSPECTIVE_PUBLIC_CONDITION_FEED_V1":
        raise ProspectiveValidationError("unsupported public condition feed format")
    if raw.get("protocol_fingerprint") != protocol.fingerprint:
        raise ProspectiveValidationError("public condition feed protocol fingerprint mismatch")
    if raw.get("contains_raw_prices") is not False or raw.get("contains_outcomes") is not False:
        raise ProspectiveValidationError("public matching feed must not expose raw prices or outcomes")
    return tuple(PublicConditionObservation(**item) for item in raw.get("conditions", ()))
