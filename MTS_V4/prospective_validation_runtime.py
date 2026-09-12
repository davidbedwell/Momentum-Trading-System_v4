from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence
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
_ET = ZoneInfo("America/New_York")
_UTC = ZoneInfo("UTC")


@dataclass(frozen=True, slots=True)
class ProspectiveExecutionPlan:
    """Executable representation of choices already frozen by the AI RD."""

    protocol_fingerprint: str
    sma_window_sessions: int
    match_search_sessions: int
    outcome_horizon_sessions: int
    terminal_finalization_lag_sessions: int
    collective_embargo: bool


@dataclass(frozen=True, slots=True)
class AuthoritativeSession:
    """One official XNAS session supplied by the validation-data custodian.

    ``mandatory_share_multiplier`` is the exact mandatory share-count multiplier
    effective on this session; use 1 when no mandatory share transformation is
    effective. A row with ``nocp=None`` still occupies an official XNAS calendar
    position and therefore still counts inside the matching search interval.
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
                f"session_date must be an ISO date: {self.session_date!r}"
            ) from exc
        if self.source_identity != "NASDAQ_NOCP":
            raise ProspectiveValidationError(
                "prospective validation requires source_identity=NASDAQ_NOCP"
            )
        if self.nocp is not None and Decimal(self.nocp) <= 0:
            raise ProspectiveValidationError("NOCP must be positive")
        if (
            self.mandatory_share_multiplier is not None
            and Decimal(self.mandatory_share_multiplier) <= 0
        ):
            raise ProspectiveValidationError(
                "mandatory_share_multiplier must be positive"
            )


@dataclass(frozen=True, slots=True)
class PublicConditionObservation:
    """Outcome-free representation released by the custodian to matching."""

    session_index: int
    session_date: str
    eligible: bool
    condition: str | None
    input_freeze_utc: str
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


def compile_execution_plan(protocol: ProspectiveValidationProtocol) -> ProspectiveExecutionPlan:
    """Resolve uniquely represented mechanics without making scientific choices.

    The compiler intentionally recognizes only the exact mechanics authored in
    the frozen protocol. If they are changed or become ambiguous it fails closed
    and returns the representation to the AI RD rather than inventing a rule.
    """

    required_fragments = (
        ("SMA20_t", protocol.authoritative_daily_close_series),
        ("immediately preceding 19 Nasdaq sessions", protocol.authoritative_daily_close_series),
        ("next nine Nasdaq sessions", protocol.matching_rule),
        ("tenth subsequent Nasdaq session", protocol.outcome_evaluable_rule),
        ("fifth XNAS session after u", protocol.outcome_evaluable_rule),
        ("greater than or equal to zero", protocol.candidate_condition),
        ("less than zero", protocol.comparison_condition),
        ("No validation outcome may be decrypted", protocol.outcome_embargo_rule),
    )
    missing = [fragment for fragment, text in required_fragments if fragment.lower() not in text.lower()]
    if missing:
        raise ProspectiveValidationError(
            "frozen protocol cannot be compiled without ambiguity; missing exact mechanics: "
            + ", ".join(missing)
        )
    if protocol.outcome_horizon_sessions != 10:
        raise ProspectiveValidationError(
            "structured outcome horizon conflicts with frozen ten-session rule"
        )
    if protocol.non_overlap_scope != "BETWEEN_TRIALS_ONLY":
        raise ProspectiveValidationError(
            "runtime currently represents only the frozen BETWEEN_TRIALS_ONLY rule"
        )
    return ProspectiveExecutionPlan(
        protocol_fingerprint=protocol.fingerprint,
        sma_window_sessions=20,
        match_search_sessions=9,
        outcome_horizon_sessions=10,
        terminal_finalization_lag_sessions=5,
        collective_embargo=True,
    )


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ProspectiveValidationError("timestamp must include timezone")
    return parsed.astimezone(_UTC)


def _freeze_time_utc(next_session_date: str) -> str:
    return (
        datetime.fromisoformat(next_session_date)
        .replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=_ET)
        .astimezone(_UTC)
        .isoformat()
    )


def _validate_series(
    sessions: Sequence[AuthoritativeSession], *, source_subject_id: str
) -> None:
    if not sessions:
        raise ProspectiveValidationError("authoritative session series is empty")
    for pos, row in enumerate(sessions):
        if row.source_subject_id != source_subject_id:
            raise ProspectiveValidationError("authoritative session subject mismatch")
        if pos:
            prior = sessions[pos - 1]
            if row.session_index != prior.session_index + 1:
                raise ProspectiveValidationError(
                    "authoritative series must contain every consecutive XNAS session"
                )
            if row.session_date <= prior.session_date:
                raise ProspectiveValidationError(
                    "authoritative session dates must be strictly increasing"
                )


def build_public_condition_feed(
    *,
    protocol: ProspectiveValidationProtocol,
    sessions: Sequence[AuthoritativeSession],
    as_of_utc: str,
) -> tuple[PublicConditionObservation, ...]:
    """Custodian step: official NOCP -> outcome-free eligibility/condition labels."""

    plan = compile_execution_plan(protocol)
    rows = tuple(sessions)
    _validate_series(rows, source_subject_id=protocol.source_subject_id)
    as_of = _parse_utc(as_of_utc)
    collection_start = _parse_utc(protocol.collection_start_utc)

    cumulative_basis: list[Decimal | None] = []
    running = Decimal("1")
    for row in rows:
        if row.mandatory_share_multiplier is None:
            cumulative_basis.append(None)
        else:
            running *= Decimal(row.mandatory_share_multiplier)
            cumulative_basis.append(running)

    result: list[PublicConditionObservation] = []
    for pos, row in enumerate(rows[:-1]):
        close_utc = (
            datetime.fromisoformat(row.session_date)
            .replace(hour=16, minute=0, second=0, microsecond=0, tzinfo=_ET)
            .astimezone(_UTC)
        )
        if close_utc <= collection_start:
            continue
        freeze_utc = _freeze_time_utc(rows[pos + 1].session_date)
        if as_of < _parse_utc(freeze_utc):
            continue

        start = pos - plan.sma_window_sessions + 1
        eligible = start >= 0
        if eligible:
            window = rows[start : pos + 1]
            eligible = all(
                item.nocp is not None
                and item.mandatory_share_multiplier is not None
                for item in window
            )
        condition: str | None = None
        metric_commitment_value = "INELIGIBLE"
        if eligible:
            current_basis = cumulative_basis[pos]
            if current_basis is None:
                eligible = False
            else:
                adjusted: list[Decimal] = []
                for offset in range(start, pos + 1):
                    historical_basis = cumulative_basis[offset]
                    historical_close = rows[offset].nocp
                    if historical_basis is None or historical_close is None:
                        eligible = False
                        adjusted = []
                        break
                    multiplier_after = current_basis / historical_basis
                    adjusted.append(Decimal(historical_close) / multiplier_after)
                if eligible:
                    sma = sum(adjusted, Decimal("0")) / Decimal(plan.sma_window_sessions)
                    metric = Decimal(row.nocp or "0") / sma - Decimal("1")
                    condition = "CANDIDATE" if metric >= 0 else "COMPARISON"
                    metric_commitment_value = format(metric, "f")

        committed = {
            "protocol_fingerprint": protocol.fingerprint,
            "session_index": row.session_index,
            "session_date": row.session_date,
            "eligible": eligible,
            "condition": condition,
            "metric": metric_commitment_value,
            "input_freeze_utc": freeze_utc,
        }
        digest = hashlib.sha256(
            json.dumps(committed, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        result.append(
            PublicConditionObservation(
                session_index=row.session_index,
                session_date=row.session_date,
                eligible=eligible,
                condition=condition,
                input_freeze_utc=freeze_utc,
                observation_commitment=digest,
            )
        )
    return tuple(result)


def derive_pairs(
    *,
    protocol: ProspectiveValidationProtocol,
    conditions: Sequence[PublicConditionObservation],
) -> tuple[MatchedPair, ...]:
    """Matching step: apply the frozen serial rule without prices or outcomes."""

    plan = compile_execution_plan(protocol)
    rows = tuple(sorted(conditions, key=lambda item: item.session_index))
    pairs: list[MatchedPair] = []
    pos = 0
    gate_closed_through = -1

    while pos < len(rows) and len(pairs) < protocol.minimum_required_trials:
        anchor = rows[pos]
        if anchor.session_index <= gate_closed_through or not anchor.eligible:
            pos += 1
            continue
        if anchor.condition not in {"CANDIDATE", "COMPARISON"}:
            raise ProspectiveValidationError("eligible observation lacks valid condition")

        match_pos: int | None = None
        for candidate_pos in range(pos + 1, len(rows)):
            other = rows[candidate_pos]
            distance = other.session_index - anchor.session_index
            if distance > plan.match_search_sessions:
                break
            if other.eligible and other.condition != anchor.condition:
                match_pos = candidate_pos
                break

        if match_pos is None:
            if not rows or rows[-1].session_index < anchor.session_index + plan.match_search_sessions:
                break
            target = anchor.session_index + plan.match_search_sessions + 1
            while pos < len(rows) and rows[pos].session_index < target:
                pos += 1
            continue

        other = rows[match_pos]
        pair = (
            MatchedPair(candidate=anchor, comparison=other)
            if anchor.condition == "CANDIDATE"
            else MatchedPair(candidate=other, comparison=anchor)
        )
        pairs.append(pair)
        gate_closed_through = max(
            pair.candidate.session_index, pair.comparison.session_index
        ) + plan.outcome_horizon_sessions
        pos = match_pos + 1
        while pos < len(rows) and rows[pos].session_index <= gate_closed_through:
            pos += 1
    return tuple(pairs)


def _find_hypothesis(package: ResearchPackage, hypothesis_id: str) -> PredictiveHypothesisRecord:
    matches = [h for h in package.predictive_hypotheses if h.hypothesis_id == hypothesis_id]
    if len(matches) != 1:
        raise ProspectiveValidationError(
            f"expected exactly one predictive hypothesis: {hypothesis_id}"
        )
    return matches[0]


def _pair_key(pair: MatchedPair) -> tuple[int, int]:
    return pair.candidate.session_index, pair.comparison.session_index


def _persisted_key(frontier: ProspectiveValidationFrontier, ordinal: int) -> tuple[int, int] | None:
    if ordinal > len(frontier.trials):
        return None
    trial = frontier.trials[ordinal - 1]
    return trial.candidate_session_index, trial.comparison_session_index


def advance_matching_runtime(
    *,
    protocol_store: JsonProspectiveValidationStore,
    research_package_store: JsonResearchPackageStore,
    rp_id: str,
    conditions: Sequence[PublicConditionObservation],
) -> RuntimeAdvanceResult:
    """Persist newly determined locks while keeping all outcomes embargoed."""

    protocol, frontier = protocol_store.load()
    package = research_package_store.load(rp_id)
    if package is None:
        raise ProspectiveValidationError(f"missing research package: {rp_id}")
    hypothesis = _find_hypothesis(package, protocol.hypothesis_id)
    protocol.validate_against_hypothesis(hypothesis)
    pairs = derive_pairs(protocol=protocol, conditions=conditions)
    newly_locked: list[str] = []

    for ordinal, pair in enumerate(pairs, 1):
        persisted = _persisted_key(frontier, ordinal)
        if persisted is not None:
            if persisted != _pair_key(pair):
                raise ProspectiveValidationError(
                    f"persisted {protocol.hypothesis_id}-T{ordinal:02d} disagrees with deterministic reconstruction"
                )
            continue
        if frontier.next_ordinal != ordinal:
            raise ProspectiveValidationError("frontier trial sequence is not contiguous")

        trial_name = f"{protocol.hypothesis_id}-T{ordinal:02d}"
        result_id = "prospective-lock:" + hashlib.sha256(
            (
                protocol.fingerprint
                + "|"
                + trial_name
                + "|"
                + pair.candidate.observation_commitment
                + "|"
                + pair.comparison.observation_commitment
            ).encode("utf-8")
        ).hexdigest()
        statement = (
            f"{protocol.frozen_hypothesis_statement} Locked {trial_name}: "
            f"candidate={pair.candidate.session_date}; comparison={pair.comparison.session_date}."
        )
        frontier, updated_hypothesis = frontier.lock_trial(
            prediction_result_id=result_id,
            prediction_statement=statement,
            candidate_session_index=pair.candidate.session_index,
            comparison_session_index=pair.comparison.session_index,
            prediction_contains_future_information=False,
            hypothesis=hypothesis,
        )
        hypotheses = list(package.predictive_hypotheses)
        h_index = next(
            i for i, item in enumerate(hypotheses) if item.hypothesis_id == hypothesis.hypothesis_id
        )
        hypotheses[h_index] = updated_hypothesis
        package = package._evolve(predictive_hypotheses=tuple(hypotheses))
        hypothesis = updated_hypothesis
        newly_locked.append(trial_name)

    if newly_locked:
        # Save RP first; if the frontier write subsequently fails, deterministic
        # reconstruction on the next run detects the already locked RP trial and
        # refuses divergence rather than silently spending or reordering science.
        research_package_store.save(package)
        protocol_store.save(protocol=protocol, frontier=frontier)

    next_id = (
        f"{protocol.hypothesis_id}-T{frontier.next_ordinal:02d}"
        if frontier.next_ordinal <= frontier.required_trials
        else None
    )
    gate = None
    if frontier.trials:
        last = frontier.trials[-1]
        gate = max(last.candidate_session_index, last.comparison_session_index) + protocol.outcome_horizon_sessions
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
            "authoritative snapshot must be an object containing sessions[]"
        )
    return tuple(AuthoritativeSession(**dict(item)) for item in raw["sessions"])


def save_public_condition_feed(
    path: str | Path,
    *,
    protocol: ProspectiveValidationProtocol,
    as_of_utc: str,
    conditions: Sequence[PublicConditionObservation],
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
    temporary.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(target)


def load_public_condition_feed(
    path: str | Path, *, protocol: ProspectiveValidationProtocol
) -> tuple[PublicConditionObservation, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("format") != "MTS_V4_PROSPECTIVE_PUBLIC_CONDITION_FEED_V1":
        raise ProspectiveValidationError("unsupported public condition feed format")
    if raw.get("protocol_fingerprint") != protocol.fingerprint:
        raise ProspectiveValidationError("condition feed protocol fingerprint mismatch")
    if raw.get("contains_raw_prices") is not False or raw.get("contains_outcomes") is not False:
        raise ProspectiveValidationError(
            "matching feed must not expose raw prices or outcomes"
        )
    return tuple(PublicConditionObservation(**item) for item in raw.get("conditions", ()))
