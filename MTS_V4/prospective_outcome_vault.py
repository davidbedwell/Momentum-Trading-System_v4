from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, getcontext
import hashlib
import json
import os
from pathlib import Path
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from cryptography.fernet import Fernet, InvalidToken

from .prospective_validation import (
    JsonProspectiveValidationStore,
    ProspectiveValidationError,
)
from .prospective_validation_runtime import (
    AuthoritativeSession,
    compile_execution_plan,
)
from .research_package import PredictiveHypothesisRecord, ResearchPackage
from .research_package_store import JsonResearchPackageStore


getcontext().prec = 50
_ET = ZoneInfo("America/New_York")
_UTC = ZoneInfo("UTC")
_VAULT_FORMAT = "MTS_V4_PROSPECTIVE_ENCRYPTED_OUTCOME_VAULT_V1"


@dataclass(frozen=True, slots=True)
class SealResult:
    locked_trials: int
    sealed_trials: int
    newly_sealed_trials: int
    release_ready: bool


@dataclass(frozen=True, slots=True)
class ReleaseResult:
    status: str
    completed_trials: int
    success_count: int | None
    failure_count: int | None
    success_rate: float | None
    hypothesis_status: str


def generate_vault_key() -> bytes:
    return Fernet.generate_key()


def write_new_vault_key(path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ProspectiveValidationError(f"vault key already exists: {target}")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(generate_vault_key() + b"\n")
    except Exception:
        target.unlink(missing_ok=True)
        raise


def load_vault_key(path: str | Path) -> bytes:
    target = Path(path)
    if not target.exists():
        raise ProspectiveValidationError(f"vault key does not exist: {target}")
    key = target.read_bytes().strip()
    try:
        Fernet(key)
    except Exception as exc:
        raise ProspectiveValidationError("invalid Fernet vault key") from exc
    return key


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ProspectiveValidationError("timestamp must include timezone")
    return parsed.astimezone(_UTC)


def _nine_am_utc(session_date: str) -> datetime:
    return (
        datetime.fromisoformat(session_date)
        .replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=_ET)
        .astimezone(_UTC)
    )


def _read_vault(path: Path, *, protocol_fingerprint: str) -> dict[str, object]:
    if not path.exists():
        return {
            "format": _VAULT_FORMAT,
            "protocol_fingerprint": protocol_fingerprint,
            "sealed_records": {},
        }
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("format") != _VAULT_FORMAT:
        raise ProspectiveValidationError("unsupported outcome vault format")
    if raw.get("protocol_fingerprint") != protocol_fingerprint:
        raise ProspectiveValidationError("outcome vault protocol fingerprint mismatch")
    records = raw.get("sealed_records")
    if not isinstance(records, Mapping):
        raise ProspectiveValidationError("outcome vault sealed_records must be an object")
    return dict(raw)


def _write_vault(path: Path, document: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)
    os.chmod(path, 0o600)


def _validate_series(sessions: Sequence[AuthoritativeSession], source_subject_id: str) -> None:
    if not sessions:
        raise ProspectiveValidationError("authoritative session series is empty")
    for pos, row in enumerate(sessions):
        if row.source_subject_id != source_subject_id:
            raise ProspectiveValidationError("authoritative session subject mismatch")
        if pos:
            prior = sessions[pos - 1]
            if row.session_index != prior.session_index + 1:
                raise ProspectiveValidationError(
                    "outcome custody requires every consecutive XNAS session"
                )
            if row.session_date <= prior.session_date:
                raise ProspectiveValidationError("XNAS session dates are not monotonic")


def _cumulative_basis(sessions: Sequence[AuthoritativeSession]) -> dict[int, Decimal | None]:
    running = Decimal("1")
    result: dict[int, Decimal | None] = {}
    for row in sessions:
        if row.mandatory_share_multiplier is None:
            result[row.session_index] = None
        else:
            running *= Decimal(row.mandatory_share_multiplier)
            result[row.session_index] = running
    return result


def _split_continuity_return(
    *,
    baseline: AuthoritativeSession,
    terminal: AuthoritativeSession,
    basis: Mapping[int, Decimal | None],
) -> Decimal | None:
    if baseline.nocp is None or terminal.nocp is None:
        return None
    base_basis = basis.get(baseline.session_index)
    terminal_basis = basis.get(terminal.session_index)
    if base_basis is None or terminal_basis is None:
        return None
    multiplier = terminal_basis / base_basis
    return Decimal(terminal.nocp) * multiplier / Decimal(baseline.nocp) - Decimal("1")


def seal_available_outcomes(
    *,
    validation_store: JsonProspectiveValidationStore,
    sessions: Sequence[AuthoritativeSession],
    as_of_utc: str,
    vault_path: str | Path,
    vault_key: bytes,
) -> SealResult:
    """Custodian-only step: encrypt matured outcomes without exposing their values."""

    protocol, frontier = validation_store.load()
    plan = compile_execution_plan(protocol)
    rows = tuple(sessions)
    _validate_series(rows, protocol.source_subject_id)
    by_index = {row.session_index: row for row in rows}
    basis = _cumulative_basis(rows)
    as_of = _parse_utc(as_of_utc)
    target = Path(vault_path)
    vault = _read_vault(target, protocol_fingerprint=protocol.fingerprint)
    records = dict(vault.get("sealed_records", {}))
    fernet = Fernet(vault_key)
    newly_sealed = 0

    for trial in frontier.trials:
        if trial.trial_id in records:
            continue
        later_baseline = max(trial.candidate_session_index, trial.comparison_session_index)
        candidate_terminal_index = trial.candidate_session_index + plan.outcome_horizon_sessions
        comparison_terminal_index = trial.comparison_session_index + plan.outcome_horizon_sessions
        finalization_index = later_baseline + plan.outcome_horizon_sessions + plan.terminal_finalization_lag_sessions
        finalization_row = by_index.get(finalization_index)
        if finalization_row is None or as_of < _nine_am_utc(finalization_row.session_date):
            continue

        candidate_base = by_index.get(trial.candidate_session_index)
        comparison_base = by_index.get(trial.comparison_session_index)
        candidate_terminal = by_index.get(candidate_terminal_index)
        comparison_terminal = by_index.get(comparison_terminal_index)
        evaluable = all(
            item is not None
            for item in (
                candidate_base,
                comparison_base,
                candidate_terminal,
                comparison_terminal,
            )
        )
        candidate_return: Decimal | None = None
        comparison_return: Decimal | None = None
        if evaluable:
            candidate_return = _split_continuity_return(
                baseline=candidate_base,  # type: ignore[arg-type]
                terminal=candidate_terminal,  # type: ignore[arg-type]
                basis=basis,
            )
            comparison_return = _split_continuity_return(
                baseline=comparison_base,  # type: ignore[arg-type]
                terminal=comparison_terminal,  # type: ignore[arg-type]
                basis=basis,
            )
            evaluable = candidate_return is not None and comparison_return is not None

        success = (
            bool(candidate_return > comparison_return)
            if evaluable and candidate_return is not None and comparison_return is not None
            else None
        )
        outcome_id_material = (
            protocol.fingerprint
            + "|"
            + trial.trial_id
            + "|"
            + str(candidate_return)
            + "|"
            + str(comparison_return)
            + "|"
            + str(evaluable)
        )
        plaintext = {
            "trial_id": trial.trial_id,
            "evaluable": evaluable,
            "candidate_return": str(candidate_return) if candidate_return is not None else None,
            "comparison_return": str(comparison_return) if comparison_return is not None else None,
            "success": success,
            "outcome_result_id": "prospective-outcome:"
            + hashlib.sha256(outcome_id_material.encode("utf-8")).hexdigest(),
            "finalization_session_index": finalization_index,
            "sealed_at_utc": as_of.isoformat(),
        }
        records[trial.trial_id] = fernet.encrypt(
            json.dumps(plaintext, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")
        newly_sealed += 1

    vault = {
        "format": _VAULT_FORMAT,
        "protocol_fingerprint": protocol.fingerprint,
        "cipher": "FERNET_AES128_CBC_HMAC_SHA256",
        "collective_embargo": True,
        "sealed_records": records,
    }
    _write_vault(target, vault)
    return SealResult(
        locked_trials=len(frontier.trials),
        sealed_trials=len(records),
        newly_sealed_trials=newly_sealed,
        release_ready=(
            len(frontier.trials) == frontier.required_trials
            and len(records) == frontier.required_trials
        ),
    )


def _find_hypothesis(package: ResearchPackage, hypothesis_id: str) -> tuple[int, PredictiveHypothesisRecord]:
    matches = [
        (index, item)
        for index, item in enumerate(package.predictive_hypotheses)
        if item.hypothesis_id == hypothesis_id
    ]
    if len(matches) != 1:
        raise ProspectiveValidationError(
            f"expected exactly one predictive hypothesis: {hypothesis_id}"
        )
    return matches[0]


def release_collective_outcomes(
    *,
    validation_store: JsonProspectiveValidationStore,
    research_package_store: JsonResearchPackageStore,
    rp_id: str,
    vault_path: str | Path,
    vault_key: bytes,
) -> ReleaseResult:
    """Lift the embargo once, only after all first 20 trial records are sealed."""

    protocol, frontier = validation_store.load()
    package = research_package_store.load(rp_id)
    if package is None:
        raise ProspectiveValidationError(f"missing research package: {rp_id}")
    h_index, hypothesis = _find_hypothesis(package, protocol.hypothesis_id)
    if len(frontier.trials) != frontier.required_trials:
        raise ProspectiveValidationError("collective embargo remains active: fewer than 20 trials locked")

    vault = _read_vault(Path(vault_path), protocol_fingerprint=protocol.fingerprint)
    records = dict(vault.get("sealed_records", {}))
    expected_ids = [trial.trial_id for trial in frontier.trials]
    if set(records) != set(expected_ids):
        raise ProspectiveValidationError(
            "collective embargo remains active: not every locked trial has a sealed outcome"
        )

    fernet = Fernet(vault_key)
    plaintext_records: list[dict[str, object]] = []
    for trial_id in expected_ids:
        try:
            payload = fernet.decrypt(str(records[trial_id]).encode("ascii"))
        except InvalidToken as exc:
            raise ProspectiveValidationError("outcome vault decryption failed") from exc
        record = json.loads(payload.decode("utf-8"))
        if record.get("trial_id") != trial_id:
            raise ProspectiveValidationError("decrypted outcome trial identity mismatch")
        plaintext_records.append(record)

    if any(record.get("evaluable") is not True for record in plaintext_records):
        return ReleaseResult(
            status="INCONCLUSIVE_REQUIRES_GOVERNANCE",
            completed_trials=0,
            success_count=None,
            failure_count=None,
            success_rate=None,
            hypothesis_status=hypothesis.status,
        )

    updated_frontier = frontier
    updated_hypothesis = hypothesis
    for record in plaintext_records:
        updated_frontier, updated_hypothesis = updated_frontier.record_outcome(
            trial_id_value=str(record["trial_id"]),
            outcome_result_id=str(record["outcome_result_id"]),
            success=bool(record["success"]),
            current_session_index=int(record["finalization_session_index"]),
            hypothesis=updated_hypothesis,
        )

    hypotheses = list(package.predictive_hypotheses)
    hypotheses[h_index] = updated_hypothesis
    updated_package = package._evolve(predictive_hypotheses=tuple(hypotheses))
    research_package_store.save(updated_package)
    validation_store.save(protocol=protocol, frontier=updated_frontier)

    return ReleaseResult(
        status="RELEASED",
        completed_trials=len(updated_hypothesis.trials),
        success_count=updated_hypothesis.success_count,
        failure_count=updated_hypothesis.failure_count,
        success_rate=updated_hypothesis.success_rate,
        hypothesis_status=updated_hypothesis.status,
    )
