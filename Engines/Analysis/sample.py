from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .canonical import semantic_fingerprint
from .overlap import EventWindow, OverlapPolicy, OverlapService, event_from_mapping
from .temporal import (
    InformationClass,
    TemporalIntegrityService,
    TimeInterval,
    interval_from_mapping,
    parse_timestamp,
)


@dataclass(frozen=True, slots=True)
class SampleSpecification:
    eligible_universe: Mapping[str, Any] = field(default_factory=dict)
    date_range: Mapping[str, Any] = field(default_factory=dict)
    inclusion_rules: tuple[Mapping[str, Any], ...] = ()
    exclusion_rules: tuple[Mapping[str, Any], ...] = ()
    event_definition: Mapping[str, Any] = field(default_factory=dict)
    outcome_definition: Mapping[str, Any] = field(default_factory=dict)
    comparison_definition: Mapping[str, Any] = field(default_factory=dict)
    missing_data_policy: str = "EXCLUDE_REQUIRED_MISSING"
    overlap_policy: Mapping[str, Any] = field(default_factory=lambda: {"policy": "ALLOW"})
    selection_information_policy: Mapping[str, Any] = field(default_factory=dict)
    research_mode: str = "EXPLORATORY"
    version: str = "sample-construction-v1"

    def to_payload(self) -> dict[str, Any]:
        return {
            "eligible_universe": dict(self.eligible_universe),
            "date_range": dict(self.date_range),
            "inclusion_rules": [dict(rule) for rule in self.inclusion_rules],
            "exclusion_rules": [dict(rule) for rule in self.exclusion_rules],
            "event_definition": dict(self.event_definition),
            "outcome_definition": dict(self.outcome_definition),
            "comparison_definition": dict(self.comparison_definition),
            "missing_data_policy": self.missing_data_policy,
            "overlap_policy": dict(self.overlap_policy),
            "selection_information_policy": dict(self.selection_information_policy),
            "research_mode": self.research_mode,
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class SampleRecord:
    eligible_count: int
    included_count: int
    excluded_count: int
    exclusion_counts_by_reason: Mapping[str, int]
    included_observation_identity: tuple[str, ...]
    time_range: Mapping[str, Any]
    group_membership: Mapping[str, tuple[str, ...]]
    missing_data_treatment: str
    overlap_treatment: Mapping[str, Any]
    future_information_usage: Mapping[str, Any]
    sample_fingerprint: str
    specification_version: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "eligible_count": self.eligible_count,
            "included_count": self.included_count,
            "excluded_count": self.excluded_count,
            "exclusion_counts_by_reason": dict(self.exclusion_counts_by_reason),
            "included_observation_identity": list(self.included_observation_identity),
            "time_range": dict(self.time_range),
            "group_membership": {
                key: list(value) for key, value in sorted(self.group_membership.items())
            },
            "missing_data_treatment": self.missing_data_treatment,
            "overlap_treatment": dict(self.overlap_treatment),
            "future_information_usage": dict(self.future_information_usage),
            "sample_fingerprint": self.sample_fingerprint,
            "specification_version": self.specification_version,
        }


@dataclass(frozen=True, slots=True)
class ConstructedSample:
    records: tuple[Mapping[str, Any], ...]
    record: SampleRecord


class SampleConstructionError(ValueError):
    pass


class SampleConstructor:
    """Deterministic Phase C sample constructor for governed row-oriented inputs."""

    def __init__(
        self,
        *,
        temporal: TemporalIntegrityService | None = None,
        overlap: OverlapService | None = None,
    ) -> None:
        self.temporal = temporal or TemporalIntegrityService()
        self.overlap = overlap or OverlapService()

    def construct(
        self,
        records: Sequence[Mapping[str, Any]],
        specification: SampleSpecification,
        *,
        timestamp_column: str = "date",
        identity_columns: Sequence[str] = ("ticker", "date"),
        required_columns: Sequence[str] = (),
        information_classes: Mapping[str, InformationClass | str] | None = None,
        predictor_columns: Sequence[str] = (),
        selection_columns: Sequence[str] = (),
        discovery_interval: TimeInterval | None = None,
        validation_interval: TimeInterval | None = None,
        holdout_interval: TimeInterval | None = None,
        protected_usage: str = "DISCOVERY",
        event_windows: Sequence[Mapping[str, Any] | EventWindow] = (),
    ) -> ConstructedSample:
        information_classes = information_classes or {}
        temporal_report = self.temporal.validate_feature_roles(
            information_classes=information_classes,
            predictor_columns=predictor_columns,
            selection_columns=selection_columns,
        )

        eligible = [dict(row) for row in records]
        exclusion_counts: dict[str, int] = {}
        filtered: list[dict[str, Any]] = []

        date_interval = interval_from_mapping(specification.date_range, label="sample_date_range")

        for row in eligible:
            reason = self._exclusion_reason(
                row,
                timestamp_column=timestamp_column,
                required_columns=required_columns,
                date_interval=date_interval,
                inclusion_rules=specification.inclusion_rules,
                exclusion_rules=specification.exclusion_rules,
                missing_data_policy=specification.missing_data_policy,
            )
            if reason is not None:
                exclusion_counts[reason] = exclusion_counts.get(reason, 0) + 1
                continue
            filtered.append(row)

        timestamps = [row[timestamp_column] for row in filtered]
        self.temporal.validate_protected_usage(
            timestamps,
            usage=protected_usage,
            discovery_interval=discovery_interval,
            validation_interval=validation_interval,
            holdout_interval=holdout_interval,
        )

        overlap_payload: dict[str, Any] = {
            "policy": specification.overlap_policy.get("policy", "ALLOW"),
            "version": self.overlap.VERSION,
            "excluded_event_ids": [],
        }
        if event_windows:
            events = tuple(
                value if isinstance(value, EventWindow) else event_from_mapping(value)
                for value in event_windows
            )
            result = self.overlap.apply(
                events,
                policy=str(specification.overlap_policy.get("policy", "ALLOW")),
                exclusion_window_days=int(
                    specification.overlap_policy.get("exclusion_window_days", 0)
                ),
            )
            overlap_payload = result.to_payload()

        ordered = tuple(
            sorted(
                filtered,
                key=lambda row: (
                    parse_timestamp(row[timestamp_column]),
                    self._identity(row, identity_columns),
                ),
            )
        )
        identities = tuple(self._identity(row, identity_columns) for row in ordered)

        group_membership = self._group_membership(
            ordered,
            specification.comparison_definition,
            identity_columns,
        )

        scientific_manifest = {
            "specification": specification.to_payload(),
            "included_observation_identity": list(identities),
            "exclusion_counts_by_reason": exclusion_counts,
            "overlap_treatment": overlap_payload,
            "future_information_usage": temporal_report.to_payload(),
        }
        fingerprint = semantic_fingerprint(scientific_manifest)

        time_range = {}
        if ordered:
            parsed = [parse_timestamp(row[timestamp_column]) for row in ordered]
            time_range = {
                "start": min(parsed).isoformat().replace("+00:00", "Z"),
                "end": max(parsed).isoformat().replace("+00:00", "Z"),
            }

        sample_record = SampleRecord(
            eligible_count=len(eligible),
            included_count=len(ordered),
            excluded_count=len(eligible) - len(ordered),
            exclusion_counts_by_reason=dict(sorted(exclusion_counts.items())),
            included_observation_identity=identities,
            time_range=time_range,
            group_membership=group_membership,
            missing_data_treatment=specification.missing_data_policy,
            overlap_treatment=overlap_payload,
            future_information_usage=temporal_report.to_payload(),
            sample_fingerprint=fingerprint,
            specification_version=specification.version,
        )
        return ConstructedSample(records=ordered, record=sample_record)

    @staticmethod
    def _identity(row: Mapping[str, Any], identity_columns: Sequence[str]) -> str:
        values = []
        for column in identity_columns:
            if column in row:
                values.append(f"{column}={row[column]}")
        if not values:
            raise SampleConstructionError("No configured identity columns exist in row")
        return "|".join(values)

    @staticmethod
    def _matches_rule(row: Mapping[str, Any], rule: Mapping[str, Any]) -> bool:
        column = str(rule["column"])
        op = str(rule.get("op", "eq")).lower()
        expected = rule.get("value")
        actual = row.get(column)
        if op == "eq":
            return actual == expected
        if op == "ne":
            return actual != expected
        if op == "gt":
            return actual is not None and actual > expected
        if op == "gte":
            return actual is not None and actual >= expected
        if op == "lt":
            return actual is not None and actual < expected
        if op == "lte":
            return actual is not None and actual <= expected
        if op == "in":
            return actual in expected
        if op == "not_in":
            return actual not in expected
        if op == "is_null":
            return actual is None
        if op == "not_null":
            return actual is not None
        raise SampleConstructionError(f"Unsupported sample rule op: {op}")

    def _exclusion_reason(
        self,
        row: Mapping[str, Any],
        *,
        timestamp_column: str,
        required_columns: Sequence[str],
        date_interval: TimeInterval | None,
        inclusion_rules: Sequence[Mapping[str, Any]],
        exclusion_rules: Sequence[Mapping[str, Any]],
        missing_data_policy: str,
    ) -> str | None:
        if timestamp_column not in row:
            return f"MISSING_TIMESTAMP:{timestamp_column}"

        if date_interval is not None and not date_interval.contains(parse_timestamp(row[timestamp_column])):
            return "OUTSIDE_DATE_RANGE"

        if missing_data_policy == "EXCLUDE_REQUIRED_MISSING":
            missing = [column for column in required_columns if row.get(column) is None]
            if missing:
                return "MISSING_REQUIRED:" + ",".join(sorted(missing))
        elif missing_data_policy not in {"ALLOW", "EXCLUDE_REQUIRED_MISSING"}:
            raise SampleConstructionError(
                f"Unsupported missing_data_policy: {missing_data_policy}"
            )

        for index, rule in enumerate(inclusion_rules):
            if not self._matches_rule(row, rule):
                return str(rule.get("reason", f"INCLUSION_RULE_{index}_FAILED"))

        for index, rule in enumerate(exclusion_rules):
            if self._matches_rule(row, rule):
                return str(rule.get("reason", f"EXCLUSION_RULE_{index}_MATCHED"))

        return None

    def _group_membership(
        self,
        rows: Sequence[Mapping[str, Any]],
        definition: Mapping[str, Any],
        identity_columns: Sequence[str],
    ) -> dict[str, tuple[str, ...]]:
        if not definition:
            return {}
        groups = definition.get("groups", {})
        result: dict[str, tuple[str, ...]] = {}
        for group_name, rule in sorted(groups.items()):
            members = tuple(
                self._identity(row, identity_columns)
                for row in rows
                if self._matches_rule(row, rule)
            )
            result[str(group_name)] = members
        return result
