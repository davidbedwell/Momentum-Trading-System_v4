from __future__ import annotations

import hashlib
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
