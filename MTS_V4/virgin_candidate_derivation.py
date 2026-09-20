from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import pyarrow.parquet as pq

from .universe_membership import load_membership_csv
from .universe_scientific_partition import ScientificCohort, load_frozen_partition
from .virgin_equivalence import EquivalenceProtocolError, VirginCandidate


def _require_file(path: str | Path, label: str) -> Path:
    value = Path(path).expanduser().resolve()
    if not value.is_file():
        raise EquivalenceProtocolError(f"{label} does not exist: {value}")
    return value


def _require_dir(path: str | Path, label: str) -> Path:
    value = Path(path).expanduser().resolve()
    if not value.is_dir():
        raise EquivalenceProtocolError(f"{label} does not exist: {value}")
    return value


def _current_ticker_by_security(membership_csv: str | Path) -> dict[str, str]:
    intervals = load_membership_csv(_require_file(membership_csv, "membership CSV")).intervals()
    by_security: dict[str, list[object]] = {}
    for interval in intervals:
        by_security.setdefault(interval.security_id, []).append(interval)
    current: dict[str, str] = {}
    for security_id, rows in by_security.items():
        open_rows = [row for row in rows if row.end_date is None]
        chosen = max(open_rows or rows, key=lambda row: row.start_date)
        current[security_id] = chosen.ticker.upper()
    return current


def _load_json(path: Path, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise EquivalenceProtocolError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, Mapping):
        raise EquivalenceProtocolError(f"{label} must contain one JSON object: {path}")
    return value


def _prior_sol_security_ids(paths: Sequence[str | Path]) -> set[str]:
    exposed: set[str] = set()
    for raw_path in paths:
        path = _require_file(raw_path, "prior-Sol exposure audit")
        document = _load_json(path, "prior-Sol exposure audit")
        if document.get("format") != "MTS_V4_UNIVERSE_PARTITION_PRIOR_SOL_EXPOSURE_REPAIR_V1":
            raise EquivalenceProtocolError(f"unsupported prior-Sol exposure audit: {path}")
        values = document.get("prior_exposed_security_ids")
        if not isinstance(values, list):
            raise EquivalenceProtocolError(f"prior-Sol audit lacks security IDs: {path}")
        exposed.update(str(value) for value in values)
    return exposed


def _subject_researched_from_ledgers(
    paths: Sequence[str | Path], *, security_to_ticker: Mapping[str, str]
) -> set[str]:
    researched: set[str] = set()
    reverse = {ticker.upper(): security_id for security_id, ticker in security_to_ticker.items()}
    for raw_path in paths:
        path = _require_file(raw_path, "scientific exposure ledger")
        document = _load_json(path, "scientific exposure ledger")
        if document.get("format") != "MTS_V4_UNIVERSE_SCIENTIFIC_EXPOSURE_V1":
            raise EquivalenceProtocolError(f"unsupported exposure ledger: {path}")
        exposures = document.get("exposures")
        if not isinstance(exposures, Mapping):
            raise EquivalenceProtocolError(f"exposure ledger lacks exposures: {path}")
        values = exposures.get("SUBJECT_RESEARCHED")
        if not isinstance(values, list):
            raise EquivalenceProtocolError(f"exposure ledger lacks SUBJECT_RESEARCHED: {path}")
        for value in values:
            identity = str(value)
            if identity in security_to_ticker:
                researched.add(identity)
            elif identity.upper() in reverse:
                researched.add(reverse[identity.upper()])
            else:
                raise EquivalenceProtocolError(
                    f"SUBJECT_RESEARCHED identity cannot be mapped to partition security: {identity}"
                )
    return researched


def _subject_ids_from_research_root(root: str | Path) -> set[str]:
    root_path = _require_dir(root, "research artifact root")
    subjects: set[str] = set()

    for path in sorted(root_path.glob("mts-v4-*/**/research_packages/*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise EquivalenceProtocolError(f"unreadable research package: {path}") from exc
        if not isinstance(raw, Mapping):
            raise EquivalenceProtocolError(f"invalid research package document: {path}")
        package = raw.get("research_package") if raw.get("format") == "MTS_V4_RESEARCH_PACKAGE_V1" else raw
        if isinstance(package, Mapping):
            subject_id = package.get("subject_id")
            if isinstance(subject_id, str) and subject_id.strip():
                subjects.add(subject_id.strip().upper())

    for path in sorted(root_path.glob("mts-v4-*/**/research_nexus.json")):
        document = _load_json(path, "research Nexus")
        raw_subjects = document.get("subjects", [])
        if not isinstance(raw_subjects, list):
            raise EquivalenceProtocolError(f"research Nexus subjects are invalid: {path}")
        for item in raw_subjects:
            if not isinstance(item, Mapping):
                raise EquivalenceProtocolError(f"invalid research Nexus subject entry: {path}")
            subject_id = item.get("subject_id")
            if isinstance(subject_id, str) and subject_id.strip():
                subjects.add(subject_id.strip().upper())
    return subjects


def _available_security_ids(derived_market_root: str | Path) -> set[str]:
    root = _require_dir(derived_market_root, "derived-market root")
    manifest = _load_json(root / "manifest.json", "derived-market manifest")
    if manifest.get("format") != "MTS_V4_DERIVED_MARKET_STORE_V1":
        raise EquivalenceProtocolError("unsupported derived-market manifest")
    streams = manifest.get("streams")
    if not isinstance(streams, Mapping) or not streams:
        raise EquivalenceProtocolError("derived-market manifest contains no streams")
    available: set[str] = set()
    files_seen = 0
    for stream in streams.values():
        if not isinstance(stream, Mapping):
            raise EquivalenceProtocolError("invalid derived-market stream")
        updates = stream.get("updates")
        if not isinstance(updates, list):
            raise EquivalenceProtocolError("derived-market stream lacks updates")
        for update in updates:
            if not isinstance(update, Mapping) or not isinstance(update.get("file_name"), str):
                raise EquivalenceProtocolError("derived-market update lacks file_name")
            parquet_path = root / str(update["file_name"])
            if not parquet_path.is_file():
                raise EquivalenceProtocolError(f"derived-market update file missing: {parquet_path}")
            table = pq.read_table(parquet_path, columns=["security_id"])
            available.update(str(value) for value in table.column("security_id").to_pylist() if value)
            files_seen += 1
    if files_seen == 0:
        raise EquivalenceProtocolError("derived-market manifest references no update files")
    return available


def derive_virgin_candidates(
    *,
    partition_path: str | Path,
    membership_csv: str | Path,
    prior_sol_audits: Sequence[str | Path],
    exposure_ledgers: Sequence[str | Path],
    research_roots: Sequence[str | Path],
    derived_market_root: str | Path,
) -> tuple[VirginCandidate, ...]:
    """Derive candidate eligibility from authoritative persisted MTS state.

    This function deliberately has no hand-authored ticker allow-list. Missing
    authoritative inputs fail closed.
    """
    partition = load_frozen_partition(_require_file(partition_path, "scientific partition"))
    security_to_ticker = _current_ticker_by_security(membership_csv)
    partition_ids = set(partition.all_security_ids)
    if set(security_to_ticker) != partition_ids:
        raise EquivalenceProtocolError(
            "membership identities do not exactly cover the frozen scientific partition"
        )

    prior_sol = _prior_sol_security_ids(prior_sol_audits)
    ledger_researched = _subject_researched_from_ledgers(
        exposure_ledgers, security_to_ticker=security_to_ticker
    )
    prior_subject_ids: set[str] = set()
    for root in research_roots:
        prior_subject_ids.update(_subject_ids_from_research_root(root))

    ticker_to_security = {ticker.upper(): security_id for security_id, ticker in security_to_ticker.items()}
    artifact_researched: set[str] = set()
    unknown_subjects: set[str] = set()
    for subject in prior_subject_ids:
        security_id = ticker_to_security.get(subject)
        if security_id is not None:
            artifact_researched.add(security_id)
        elif subject in partition_ids:
            artifact_researched.add(subject)
        else:
            # Non-universe subjects are irrelevant; partition members cannot be
            # treated as virgin merely because an in-universe identity is unknown.
            unknown_subjects.add(subject)

    available = _available_security_ids(derived_market_root)
    discovery = set(partition.members(ScientificCohort.DISCOVERY))
    candidates = []
    for security_id in sorted(partition_ids):
        candidates.append(
            VirginCandidate(
                subject_id=security_to_ticker[security_id],
                partition="DISCOVERY" if security_id in discovery else (
                    "VERIFICATION_A"
                    if security_id in set(partition.members(ScientificCohort.VERIFICATION_A))
                    else "VERIFICATION_B"
                ),
                prior_sol_exposure=security_id in prior_sol,
                prior_gemini_exposure=False,
                prior_campaign_exposure=security_id in ledger_researched or security_id in artifact_researched,
                starting_data_available=security_id in available,
            )
        )
    return tuple(candidates)


def candidate_manifest(candidates: Iterable[VirginCandidate]) -> list[dict[str, object]]:
    return [
        {
            "subject_id": item.subject_id,
            "partition": item.partition,
            "prior_sol_exposure": item.prior_sol_exposure,
            "prior_gemini_exposure": item.prior_gemini_exposure,
            "prior_campaign_exposure": item.prior_campaign_exposure,
            "starting_data_available": item.starting_data_available,
        }
        for item in candidates
    ]
