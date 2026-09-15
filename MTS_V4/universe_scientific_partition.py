from __future__ import annotations

import hashlib
from itertools import combinations
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence


PARTITION_FORMAT = "MTS_V4_UNIVERSE_SCIENTIFIC_PARTITION_V1"


class UniverseScientificPartitionError(RuntimeError):
    pass


class ScientificCohort(str, Enum):
    DISCOVERY = "DISCOVERY"
    VERIFICATION_A = "VERIFICATION_A"
    VERIFICATION_B = "VERIFICATION_B"


class ScientificExposure(str, Enum):
    CONTEXT_ONLY = "CONTEXT_ONLY"
    DISCOVERY_OUTCOME_EXPOSED = "DISCOVERY_OUTCOME_EXPOSED"
    BLIND_VERIFICATION_EXPOSED = "BLIND_VERIFICATION_EXPOSED"
    SUBJECT_RESEARCHED = "SUBJECT_RESEARCHED"


@dataclass(frozen=True, slots=True)
class UniverseScientificPartition:
    universe_id: str
    partition_id: str
    salt_identity: str
    cohorts: Mapping[str, tuple[str, ...]]

    @property
    def all_security_ids(self) -> tuple[str, ...]:
        return tuple(
            security_id
            for cohort in ScientificCohort
            for security_id in self.cohorts[cohort.value]
        )

    def members(self, cohort: ScientificCohort | str) -> tuple[str, ...]:
        key = ScientificCohort(cohort).value
        return self.cohorts[key]

    def to_mapping(self) -> dict[str, object]:
        return {
            "format": PARTITION_FORMAT,
            "universe_id": self.universe_id,
            "partition_id": self.partition_id,
            "salt_identity": self.salt_identity,
            "cohorts": {key: list(value) for key, value in self.cohorts.items()},
        }


def create_frozen_partition(
    *,
    universe_id: str,
    security_ids: Sequence[str],
    cohort_sizes: Mapping[ScientificCohort | str, int],
    salt: str,
) -> UniverseScientificPartition:
    """Create an exact-size, deterministic partition without scientific ranking.

    Cohort sizes are caller-authorized governance inputs. Code deliberately has
    no default split and therefore cannot silently consume verification capacity.
    """

    normalized = tuple(sorted({str(item).strip() for item in security_ids if str(item).strip()}))
    if len(normalized) != len(security_ids):
        raise UniverseScientificPartitionError("security IDs must be nonblank and unique")
    if not universe_id.strip() or not salt:
        raise UniverseScientificPartitionError("universe_id and salt are required")
    sizes = {cohort.value: int(cohort_sizes.get(cohort, cohort_sizes.get(cohort.value, -1))) for cohort in ScientificCohort}
    if any(value < 0 for value in sizes.values()):
        raise UniverseScientificPartitionError("an explicit size is required for every cohort")
    if sum(sizes.values()) != len(normalized):
        raise UniverseScientificPartitionError("cohort sizes must exactly cover the supplied universe")
    ordered = sorted(
        normalized,
        key=lambda security_id: (
            hashlib.sha256(f"{salt}|{universe_id}|{security_id}".encode("utf-8")).hexdigest(),
            security_id,
        ),
    )
    cohorts: dict[str, tuple[str, ...]] = {}
    offset = 0
    for cohort in ScientificCohort:
        next_offset = offset + sizes[cohort.value]
        cohorts[cohort.value] = tuple(sorted(ordered[offset:next_offset]))
        offset = next_offset
    identity_payload = {
        "format": PARTITION_FORMAT,
        "universe_id": universe_id,
        "salt_identity": hashlib.sha256(salt.encode("utf-8")).hexdigest(),
        "cohorts": {key: list(value) for key, value in cohorts.items()},
    }
    partition_id = hashlib.sha256(
        json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return UniverseScientificPartition(
        universe_id=universe_id,
        partition_id=partition_id,
        salt_identity=identity_payload["salt_identity"],
        cohorts=cohorts,
    )


def create_stratified_frozen_partition(
    *,
    universe_id: str,
    security_ids: Sequence[str],
    cohort_sizes: Mapping[ScientificCohort | str, int],
    strata: Mapping[str, Sequence[str]],
    salt: str,
) -> tuple[UniverseScientificPartition, Mapping[str, object]]:
    """Create exact cohort totals with proportional salted assignment within strata."""
    normalized = tuple(sorted({str(item).strip() for item in security_ids if str(item).strip()}))
    if len(normalized) != len(security_ids):
        raise UniverseScientificPartitionError("security IDs must be nonblank and unique")
    if not universe_id.strip() or not salt:
        raise UniverseScientificPartitionError("universe_id and salt are required")
    if set(strata) != set(normalized):
        raise UniverseScientificPartitionError("stratification attributes must exactly cover security IDs")
    sizes = {
        cohort.value: int(cohort_sizes.get(cohort, cohort_sizes.get(cohort.value, -1)))
        for cohort in ScientificCohort
    }
    if any(value < 0 for value in sizes.values()):
        raise UniverseScientificPartitionError("an explicit size is required for every cohort")
    if sum(sizes.values()) != len(normalized):
        raise UniverseScientificPartitionError("cohort sizes must exactly cover the supplied universe")
    groups: dict[tuple[str, ...], list[str]] = {}
    for security_id in normalized:
        label = tuple(str(item).strip() for item in strata[security_id])
        if not label or any(not item for item in label):
            raise UniverseScientificPartitionError(f"blank stratification value for {security_id}")
        groups.setdefault(label, []).append(security_id)

    cohort_names = tuple(cohort.value for cohort in ScientificCohort)
    total = len(normalized)
    floors: dict[tuple[str, ...], dict[str, int]] = {}
    leftovers: dict[tuple[str, ...], int] = {}
    fractional: dict[tuple[str, ...], dict[str, int]] = {}
    for label, members in groups.items():
        n = len(members)
        floors[label] = {name: n * sizes[name] // total for name in cohort_names}
        fractional[label] = {name: (n * sizes[name]) % total for name in cohort_names}
        leftovers[label] = n - sum(floors[label].values())

    residual = {
        name: sizes[name] - sum(floors[label][name] for label in groups)
        for name in cohort_names
    }
    # Dynamic programming solves the small exact-margin apportionment problem.
    # Scores maximize proportional largest remainders; lexical ties are deterministic.
    states: dict[tuple[int, int], tuple[int, tuple[tuple[str, ...], ...], int]] = {
        (0, 0): (0, (), 0)
    }
    ordered_labels = tuple(sorted(groups))
    for label in ordered_labels:
        needed = leftovers[label]
        options = tuple(combinations(cohort_names, needed))
        next_states: dict[tuple[int, int], tuple[int, tuple[tuple[str, ...], ...], int]] = {}
        for (used_d, used_a), (score, choices, used_b) in states.items():
            for option in options:
                new_d = used_d + (ScientificCohort.DISCOVERY.value in option)
                new_a = used_a + (ScientificCohort.VERIFICATION_A.value in option)
                new_b = used_b + (ScientificCohort.VERIFICATION_B.value in option)
                if (
                    new_d > residual[ScientificCohort.DISCOVERY.value]
                    or new_a > residual[ScientificCohort.VERIFICATION_A.value]
                    or new_b > residual[ScientificCohort.VERIFICATION_B.value]
                ):
                    continue
                new_score = score + sum(fractional[label][name] for name in option)
                key = (new_d, new_a)
                candidate = (new_score, (*choices, tuple(option)), new_b)
                prior = next_states.get(key)
                if prior is None or candidate[0] > prior[0] or (
                    candidate[0] == prior[0] and candidate[1] < prior[1]
                ):
                    next_states[key] = candidate
        states = next_states
    target_key = (
        residual[ScientificCohort.DISCOVERY.value],
        residual[ScientificCohort.VERIFICATION_A.value],
    )
    solution = states.get(target_key)
    if solution is None or solution[2] != residual[ScientificCohort.VERIFICATION_B.value]:
        raise UniverseScientificPartitionError("no exact proportional stratified allocation exists")

    assignments: dict[str, list[str]] = {name: [] for name in cohort_names}
    stratum_audit: list[Mapping[str, object]] = []
    for label, extras in zip(ordered_labels, solution[1]):
        members = sorted(
            groups[label],
            key=lambda security_id: (
                hashlib.sha256(
                    f"{salt}|{universe_id}|{'|'.join(label)}|{security_id}".encode("utf-8")
                ).hexdigest(),
                security_id,
            ),
        )
        counts = {
            name: floors[label][name] + (name in extras)
            for name in cohort_names
        }
        offset = 0
        for name in cohort_names:
            assignments[name].extend(members[offset:offset + counts[name]])
            offset += counts[name]
        stratum_audit.append({
            "stratum": list(label),
            "security_count": len(members),
            "cohort_counts": counts,
        })
    cohorts = {name: tuple(sorted(values)) for name, values in assignments.items()}
    identity_payload = {
        "format": PARTITION_FORMAT,
        "universe_id": universe_id,
        "salt_identity": hashlib.sha256(salt.encode("utf-8")).hexdigest(),
        "cohorts": {key: list(value) for key, value in cohorts.items()},
    }
    partition = UniverseScientificPartition(
        universe_id=universe_id,
        partition_id=hashlib.sha256(
            json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        salt_identity=identity_payload["salt_identity"],
        cohorts=cohorts,
    )
    audit = {
        "method": "EXACT_PROPORTIONAL_STRATIFIED_SALTED_ASSIGNMENT_V1",
        "scientific_selection_or_ranking": False,
        "stratum_count": len(groups),
        "strata": stratum_audit,
    }
    return partition, audit


def load_frozen_partition(path: str | Path) -> UniverseScientificPartition:
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    if raw.get("format") != PARTITION_FORMAT:
        raise UniverseScientificPartitionError("unsupported scientific partition format")
    try:
        cohorts = {
            cohort.value: tuple(str(item) for item in raw["cohorts"][cohort.value])
            for cohort in ScientificCohort
        }
        partition = UniverseScientificPartition(
            universe_id=str(raw["universe_id"]),
            partition_id=str(raw["partition_id"]),
            salt_identity=str(raw["salt_identity"]),
            cohorts=cohorts,
        )
    except (KeyError, TypeError) as exc:
        raise UniverseScientificPartitionError("incomplete scientific partition manifest") from exc
    all_ids = partition.all_security_ids
    if not all_ids or len(all_ids) != len(set(all_ids)):
        raise UniverseScientificPartitionError("partition cohorts must be nonempty in aggregate and disjoint")
    identity_payload = {
        "format": PARTITION_FORMAT,
        "universe_id": partition.universe_id,
        "salt_identity": partition.salt_identity,
        "cohorts": {key: list(value) for key, value in partition.cohorts.items()},
    }
    expected = hashlib.sha256(
        json.dumps(identity_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if partition.partition_id != expected:
        raise UniverseScientificPartitionError("scientific partition identity does not match its content")
    return partition


def write_frozen_partition(path: str | Path, partition: UniverseScientificPartition) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = load_frozen_partition(target)
        if existing != partition:
            raise UniverseScientificPartitionError("refusing to replace an existing frozen partition")
        return
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps(partition.to_mapping(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)


def write_campaign_exposure_ledger(
    path: str | Path,
    *,
    partition: UniverseScientificPartition,
    campaign_id: str,
    context_security_ids: Sequence[str],
    outcome_security_ids: Sequence[str],
) -> None:
    """Record member exposure without equating market context with outcome use."""

    context = tuple(sorted(set(context_security_ids)))
    outcomes = tuple(sorted(set(outcome_security_ids)))
    universe = set(partition.all_security_ids)
    if not set(context).issubset(universe) or not set(outcomes).issubset(universe):
        raise UniverseScientificPartitionError("exposure ledger contains identity outside partition")
    discovery = set(partition.members(ScientificCohort.DISCOVERY))
    if not set(outcomes).issubset(discovery):
        raise UniverseScientificPartitionError("discovery runner cannot expose reserved-cohort outcomes")
    payload = {
        "format": "MTS_V4_UNIVERSE_SCIENTIFIC_EXPOSURE_V1",
        "campaign_id": campaign_id,
        "universe_id": partition.universe_id,
        "partition_id": partition.partition_id,
        "exposures": {
            ScientificExposure.CONTEXT_ONLY.value: list(context),
            ScientificExposure.DISCOVERY_OUTCOME_EXPOSED.value: list(outcomes),
            ScientificExposure.BLIND_VERIFICATION_EXPOSED.value: [],
            ScientificExposure.SUBJECT_RESEARCHED.value: [],
        },
        "reserved_unexposed": {
            ScientificCohort.VERIFICATION_A.value: list(partition.members(ScientificCohort.VERIFICATION_A)),
            ScientificCohort.VERIFICATION_B.value: list(partition.members(ScientificCohort.VERIFICATION_B)),
        },
    }
    target = Path(path)
    if target.exists():
        raise UniverseScientificPartitionError("refusing to replace campaign exposure ledger")
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)
