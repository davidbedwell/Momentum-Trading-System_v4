from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq


class DerivedMarketStoreError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class UniverseDefinition:
    universe_id: str
    description: str
    membership_source: str
    point_in_time_membership_required: bool = True
    stable_security_id_namespace: str = "MTS_SECURITY_ID"
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DerivedFeatureDefinition:
    feature_id: str
    version: str
    description: str
    dependencies: tuple[str, ...] = ()
    required_lookback_sessions: int = 0
    knowledge_timing: str = "KNOWN_BY_EFFECTIVE_DATE"
    classification: str = "PREDICTOR"
    dtype: str = "float64"
    attributes: Mapping[str, Any] = field(default_factory=dict)

    @property
    def column_name(self) -> str:
        return f"{self.feature_id}__{self.version}"


@dataclass(frozen=True, slots=True)
class DerivedFeatureSetDefinition:
    feature_set_id: str
    version: str
    description: str
    features: tuple[DerivedFeatureDefinition, ...]
    attributes: Mapping[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.feature_set_id}:{self.version}"

    @property
    def feature_columns(self) -> tuple[str, ...]:
        return tuple(feature.column_name for feature in self.features)

    @property
    def maximum_lookback_sessions(self) -> int:
        return max((feature.required_lookback_sessions for feature in self.features), default=0)


@dataclass(frozen=True, slots=True)
class DerivedMarketQuery:
    universe_id: str
    feature_set_id: str
    feature_set_version: str
    start_date: str | None = None
    end_date: str | None = None
    security_ids: tuple[str, ...] = ()
    feature_columns: tuple[str, ...] = ()
    include_ineligible: bool = False

    @property
    def feature_set_key(self) -> str:
        return f"{self.feature_set_id}:{self.feature_set_version}"

    def deterministic_id(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True, slots=True)
class DerivedMarketUpdateRecord:
    update_id: str
    universe_id: str
    feature_set_key: str
    first_effective_date: str
    last_effective_date: str
    row_count: int
    file_name: str
    published_at_utc: str
    source_lineage: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DerivedMarketState:
    universe_id: str
    feature_set_key: str
    high_water_mark: str | None
    updates: tuple[DerivedMarketUpdateRecord, ...]


@dataclass(frozen=True, slots=True)
class DerivedMarketUpdatePlan:
    universe_id: str
    feature_set_key: str
    prior_high_water_mark: str | None
    first_new_effective_date: str
    last_new_effective_date: str
    maximum_lookback_sessions: int
    suggested_calendar_lookback_days: int


class DerivedMarketStore(Protocol):
    def register_universe(self, definition: UniverseDefinition) -> None: ...
    def register_feature_set(self, definition: DerivedFeatureSetDefinition) -> None: ...
    def get_universe(self, universe_id: str) -> UniverseDefinition | None: ...
    def get_feature_set(self, feature_set_id: str, version: str) -> DerivedFeatureSetDefinition | None: ...
    def append_update(
        self,
        *,
        universe_id: str,
        feature_set_id: str,
        feature_set_version: str,
        update_id: str,
        rows: Sequence[Mapping[str, Any]],
        source_lineage: Mapping[str, Any] | None = None,
    ) -> DerivedMarketUpdateRecord: ...
    def state(
        self,
        universe_id: str,
        feature_set_id: str,
        feature_set_version: str,
    ) -> DerivedMarketState: ...
    def query(self, query: DerivedMarketQuery) -> tuple[Mapping[str, Any], ...]: ...


def plan_incremental_update(
    *,
    store: DerivedMarketStore,
    universe_id: str,
    feature_set_id: str,
    feature_set_version: str,
    first_new_effective_date: str,
    last_new_effective_date: str,
) -> DerivedMarketUpdatePlan:
    feature_set = store.get_feature_set(feature_set_id, feature_set_version)
    if feature_set is None:
        raise DerivedMarketStoreError(
            f"unknown feature set: {feature_set_id}:{feature_set_version}"
        )
    state = store.state(universe_id, feature_set_id, feature_set_version)
    maximum = feature_set.maximum_lookback_sessions
    # Trading-session lookback is intentionally converted conservatively to
    # calendar days only for source-acquisition planning. The actual feature
    # implementation remains responsible for exact trading-session semantics.
    calendar_days = max(0, int(maximum * 7 / 5) + 14)
    return DerivedMarketUpdatePlan(
        universe_id=universe_id,
        feature_set_key=feature_set.key,
        prior_high_water_mark=state.high_water_mark,
        first_new_effective_date=first_new_effective_date,
        last_new_effective_date=last_new_effective_date,
        maximum_lookback_sessions=maximum,
        suggested_calendar_lookback_days=calendar_days,
    )


def acquisition_start_for_plan(plan: DerivedMarketUpdatePlan) -> str:
    first = date.fromisoformat(plan.first_new_effective_date)
    return (first - timedelta(days=plan.suggested_calendar_lookback_days)).isoformat()


class InMemoryDerivedMarketStore:
    def __init__(self) -> None:
        self._universes: dict[str, UniverseDefinition] = {}
        self._feature_sets: dict[str, DerivedFeatureSetDefinition] = {}
        self._rows: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self._updates: dict[tuple[str, str], list[DerivedMarketUpdateRecord]] = {}

    def register_universe(self, definition: UniverseDefinition) -> None:
        if not definition.universe_id.strip():
            raise DerivedMarketStoreError("universe_id cannot be blank")
        existing = self._universes.get(definition.universe_id)
        if existing is not None and existing != definition:
            raise DerivedMarketStoreError(
                f"universe definition already exists with different content: {definition.universe_id}"
            )
        self._universes[definition.universe_id] = definition

    def register_feature_set(self, definition: DerivedFeatureSetDefinition) -> None:
        _validate_feature_set(definition)
        existing = self._feature_sets.get(definition.key)
        if existing is not None and existing != definition:
            raise DerivedMarketStoreError(
                f"feature set already exists with different content: {definition.key}"
            )
        self._feature_sets[definition.key] = definition

    def get_universe(self, universe_id: str) -> UniverseDefinition | None:
        return self._universes.get(universe_id)

    def get_feature_set(self, feature_set_id: str, version: str) -> DerivedFeatureSetDefinition | None:
        return self._feature_sets.get(f"{feature_set_id}:{version}")

    def append_update(
        self,
        *,
        universe_id: str,
        feature_set_id: str,
        feature_set_version: str,
        update_id: str,
        rows: Sequence[Mapping[str, Any]],
        source_lineage: Mapping[str, Any] | None = None,
    ) -> DerivedMarketUpdateRecord:
        feature_set = self._require_definitions(universe_id, feature_set_id, feature_set_version)
        normalized, first_date, last_date = _normalize_and_validate_rows(rows, feature_set)
        key = (universe_id, feature_set.key)
        updates = self._updates.setdefault(key, [])
        _validate_append_window(updates, update_id, first_date, last_date)
        self._rows.setdefault(key, []).extend(normalized)
        record = DerivedMarketUpdateRecord(
            update_id=update_id,
            universe_id=universe_id,
            feature_set_key=feature_set.key,
            first_effective_date=first_date,
            last_effective_date=last_date,
            row_count=len(normalized),
            file_name=f"memory://{update_id}",
            published_at_utc=datetime.now(timezone.utc).isoformat(),
            source_lineage=dict(source_lineage or {}),
        )
        updates.append(record)
        return record

    def state(self, universe_id: str, feature_set_id: str, feature_set_version: str) -> DerivedMarketState:
        key = (universe_id, f"{feature_set_id}:{feature_set_version}")
        updates = tuple(self._updates.get(key, ()))
        return DerivedMarketState(
            universe_id=universe_id,
            feature_set_key=key[1],
            high_water_mark=updates[-1].last_effective_date if updates else None,
            updates=updates,
        )

    def query(self, query: DerivedMarketQuery) -> tuple[Mapping[str, Any], ...]:
        feature_set = self._require_definitions(
            query.universe_id,
            query.feature_set_id,
            query.feature_set_version,
        )
        columns = _query_columns(query, feature_set)
        rows = self._rows.get((query.universe_id, feature_set.key), [])
        selected: list[Mapping[str, Any]] = []
        security_set = set(query.security_ids)
        for row in rows:
            if query.start_date is not None and row["effective_date"] < query.start_date:
                continue
            if query.end_date is not None and row["effective_date"] > query.end_date:
                continue
            if security_set and row["security_id"] not in security_set:
                continue
            if not query.include_ineligible and not bool(row.get("eligible", True)):
                continue
            selected.append({column: row.get(column) for column in columns})
        return tuple(selected)

    def _require_definitions(
        self,
        universe_id: str,
        feature_set_id: str,
        feature_set_version: str,
    ) -> DerivedFeatureSetDefinition:
        if universe_id not in self._universes:
            raise DerivedMarketStoreError(f"unknown universe: {universe_id}")
        feature_set = self.get_feature_set(feature_set_id, feature_set_version)
        if feature_set is None:
            raise DerivedMarketStoreError(
                f"unknown feature set: {feature_set_id}:{feature_set_version}"
            )
        return feature_set


class ParquetDerivedMarketStore:
    """Nexus-owned append-only derived market store.

    Raw market data does not enter this store. Each update writes an immutable
    Parquet file first and then atomically advances a compact manifest. Readers
    see only files referenced by the published manifest, so a failed write cannot
    expose a partial cross-section as current.
    """

    MANIFEST_FORMAT = "MTS_V4_DERIVED_MARKET_STORE_V1"

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._manifest_path = self._root / "manifest.json"
        self._root.mkdir(parents=True, exist_ok=True)
        if not self._manifest_path.exists():
            self._write_manifest(
                {
                    "format": self.MANIFEST_FORMAT,
                    "universes": {},
                    "feature_sets": {},
                    "streams": {},
                }
            )

    def register_universe(self, definition: UniverseDefinition) -> None:
        if not definition.universe_id.strip():
            raise DerivedMarketStoreError("universe_id cannot be blank")
        manifest = self._read_manifest()
        existing = manifest["universes"].get(definition.universe_id)
        payload = asdict(definition)
        if existing is not None and existing != payload:
            raise DerivedMarketStoreError(
                f"universe definition already exists with different content: {definition.universe_id}"
            )
        if existing is None:
            manifest["universes"][definition.universe_id] = payload
            self._write_manifest(manifest)

    def register_feature_set(self, definition: DerivedFeatureSetDefinition) -> None:
        _validate_feature_set(definition)
        manifest = self._read_manifest()
        payload = asdict(definition)
        existing = manifest["feature_sets"].get(definition.key)
        if existing is not None and existing != payload:
            raise DerivedMarketStoreError(
                f"feature set already exists with different content: {definition.key}"
            )
        if existing is None:
            manifest["feature_sets"][definition.key] = payload
            self._write_manifest(manifest)

    def get_universe(self, universe_id: str) -> UniverseDefinition | None:
        raw = self._read_manifest()["universes"].get(universe_id)
        return UniverseDefinition(**raw) if raw is not None else None

    def get_feature_set(self, feature_set_id: str, version: str) -> DerivedFeatureSetDefinition | None:
        raw = self._read_manifest()["feature_sets"].get(f"{feature_set_id}:{version}")
        if raw is None:
            return None
        return _feature_set_from_mapping(raw)

    def append_update(
        self,
        *,
        universe_id: str,
        feature_set_id: str,
        feature_set_version: str,
        update_id: str,
        rows: Sequence[Mapping[str, Any]],
        source_lineage: Mapping[str, Any] | None = None,
    ) -> DerivedMarketUpdateRecord:
        feature_set = self._require_definitions(universe_id, feature_set_id, feature_set_version)
        normalized, first_date, last_date = _normalize_and_validate_rows(rows, feature_set)
        manifest = self._read_manifest()
        stream_key = _stream_key(universe_id, feature_set.key)
        stream = manifest["streams"].setdefault(
            stream_key,
            {
                "universe_id": universe_id,
                "feature_set_key": feature_set.key,
                "high_water_mark": None,
                "updates": [],
            },
        )
        prior = tuple(_update_record_from_mapping(item) for item in stream["updates"])
        _validate_append_window(prior, update_id, first_date, last_date)

        stream_dir = self._root / "data" / _safe_path_component(universe_id) / _safe_path_component(feature_set.key)
        stream_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{update_id}.parquet"
        target = stream_dir / file_name
        if target.exists():
            raise DerivedMarketStoreError(f"update file already exists: {target}")
        temporary = target.with_suffix(".parquet.tmp")
        table = pa.Table.from_pylist(normalized)
        pq.write_table(table, temporary, compression="zstd")
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        temporary.replace(target)

        record = DerivedMarketUpdateRecord(
            update_id=update_id,
            universe_id=universe_id,
            feature_set_key=feature_set.key,
            first_effective_date=first_date,
            last_effective_date=last_date,
            row_count=len(normalized),
            file_name=str(target.relative_to(self._root)),
            published_at_utc=datetime.now(timezone.utc).isoformat(),
            source_lineage=dict(source_lineage or {}),
        )
        stream["updates"].append(asdict(record))
        stream["high_water_mark"] = last_date
        self._write_manifest(manifest)
        return record

    def state(self, universe_id: str, feature_set_id: str, feature_set_version: str) -> DerivedMarketState:
        feature_set_key = f"{feature_set_id}:{feature_set_version}"
        stream = self._read_manifest()["streams"].get(_stream_key(universe_id, feature_set_key))
        if stream is None:
            return DerivedMarketState(
                universe_id=universe_id,
                feature_set_key=feature_set_key,
                high_water_mark=None,
                updates=(),
            )
        updates = tuple(_update_record_from_mapping(item) for item in stream["updates"])
        return DerivedMarketState(
            universe_id=universe_id,
            feature_set_key=feature_set_key,
            high_water_mark=stream.get("high_water_mark"),
            updates=updates,
        )

    def query(self, query: DerivedMarketQuery) -> tuple[Mapping[str, Any], ...]:
        feature_set = self._require_definitions(
            query.universe_id,
            query.feature_set_id,
            query.feature_set_version,
        )
        state = self.state(query.universe_id, query.feature_set_id, query.feature_set_version)
        if not state.updates:
            return ()
        columns = _query_columns(query, feature_set)
        files = [str(self._root / update.file_name) for update in state.updates]
        dataset = ds.dataset(files, format="parquet")
        predicate = None
        if query.start_date is not None:
            predicate = ds.field("effective_date") >= query.start_date
        if query.end_date is not None:
            clause = ds.field("effective_date") <= query.end_date
            predicate = clause if predicate is None else predicate & clause
        if query.security_ids:
            clause = ds.field("security_id").isin(list(query.security_ids))
            predicate = clause if predicate is None else predicate & clause
        if not query.include_ineligible:
            clause = ds.field("eligible") == True  # noqa: E712
            predicate = clause if predicate is None else predicate & clause
        table = dataset.to_table(columns=list(columns), filter=predicate)
        return tuple(dict(row) for row in table.to_pylist())

    def _require_definitions(
        self,
        universe_id: str,
        feature_set_id: str,
        feature_set_version: str,
    ) -> DerivedFeatureSetDefinition:
        if self.get_universe(universe_id) is None:
            raise DerivedMarketStoreError(f"unknown universe: {universe_id}")
        feature_set = self.get_feature_set(feature_set_id, feature_set_version)
        if feature_set is None:
            raise DerivedMarketStoreError(
                f"unknown feature set: {feature_set_id}:{feature_set_version}"
            )
        return feature_set

    def _read_manifest(self) -> dict[str, Any]:
        document = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        if document.get("format") != self.MANIFEST_FORMAT:
            raise DerivedMarketStoreError(
                f"unsupported derived market store manifest: {document.get('format')!r}"
            )
        return document

    def _write_manifest(self, document: Mapping[str, Any]) -> None:
        temporary = self._manifest_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(document, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        temporary.replace(self._manifest_path)


def _feature_set_from_mapping(raw: Mapping[str, Any]) -> DerivedFeatureSetDefinition:
    features = tuple(
        DerivedFeatureDefinition(
            feature_id=str(item["feature_id"]),
            version=str(item["version"]),
            description=str(item["description"]),
            dependencies=tuple(item.get("dependencies", ())),
            required_lookback_sessions=int(item.get("required_lookback_sessions", 0)),
            knowledge_timing=str(item.get("knowledge_timing", "KNOWN_BY_EFFECTIVE_DATE")),
            classification=str(item.get("classification", "PREDICTOR")),
            dtype=str(item.get("dtype", "float64")),
            attributes=dict(item.get("attributes", {})),
        )
        for item in raw.get("features", ())
    )
    return DerivedFeatureSetDefinition(
        feature_set_id=str(raw["feature_set_id"]),
        version=str(raw["version"]),
        description=str(raw["description"]),
        features=features,
        attributes=dict(raw.get("attributes", {})),
    )


def _update_record_from_mapping(raw: Mapping[str, Any]) -> DerivedMarketUpdateRecord:
    return DerivedMarketUpdateRecord(
        update_id=str(raw["update_id"]),
        universe_id=str(raw["universe_id"]),
        feature_set_key=str(raw["feature_set_key"]),
        first_effective_date=str(raw["first_effective_date"]),
        last_effective_date=str(raw["last_effective_date"]),
        row_count=int(raw["row_count"]),
        file_name=str(raw["file_name"]),
        published_at_utc=str(raw["published_at_utc"]),
        source_lineage=dict(raw.get("source_lineage", {})),
    )


def _validate_feature_set(definition: DerivedFeatureSetDefinition) -> None:
    if not definition.feature_set_id.strip() or not definition.version.strip():
        raise DerivedMarketStoreError("feature_set_id and version cannot be blank")
    columns = [feature.column_name for feature in definition.features]
    if len(columns) != len(set(columns)):
        raise DerivedMarketStoreError("feature columns must be unique within a feature set")
    for feature in definition.features:
        if not feature.feature_id.strip() or not feature.version.strip():
            raise DerivedMarketStoreError("feature_id and feature version cannot be blank")
        if feature.required_lookback_sessions < 0:
            raise DerivedMarketStoreError("required_lookback_sessions cannot be negative")
        if feature.classification not in {"PREDICTOR", "OUTCOME", "CONTEXT"}:
            raise DerivedMarketStoreError(
                f"unsupported feature classification: {feature.classification}"
            )


def _normalize_and_validate_rows(
    rows: Sequence[Mapping[str, Any]],
    feature_set: DerivedFeatureSetDefinition,
) -> tuple[list[dict[str, Any]], str, str]:
    if not rows:
        raise DerivedMarketStoreError("derived market update must contain at least one row")
    required = {"security_id", "effective_date", "eligible", *feature_set.feature_columns}
    normalized: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    effective_dates: list[str] = []
    for index, raw in enumerate(rows):
        missing = sorted(required.difference(raw))
        if missing:
            raise DerivedMarketStoreError(
                f"derived market row {index} missing required columns: {tuple(missing)}"
            )
        security_id = str(raw["security_id"]).strip()
        effective_date = str(raw["effective_date"])
        if not security_id:
            raise DerivedMarketStoreError(f"derived market row {index} has blank security_id")
        date.fromisoformat(effective_date)
        identity = (security_id, effective_date)
        if identity in identities:
            raise DerivedMarketStoreError(
                f"duplicate security/effective_date inside update: {identity}"
            )
        identities.add(identity)
        effective_dates.append(effective_date)
        row = {
            "security_id": security_id,
            "effective_date": effective_date,
            "eligible": bool(raw["eligible"]),
        }
        for column in feature_set.feature_columns:
            value = raw[column]
            row[column] = None if value is None else float(value)
        normalized.append(row)
    normalized.sort(key=lambda item: (item["effective_date"], item["security_id"]))
    return normalized, min(effective_dates), max(effective_dates)


def _validate_append_window(
    updates: Sequence[DerivedMarketUpdateRecord],
    update_id: str,
    first_date: str,
    last_date: str,
) -> None:
    if not update_id.strip():
        raise DerivedMarketStoreError("update_id cannot be blank")
    if any(update.update_id == update_id for update in updates):
        raise DerivedMarketStoreError(f"update_id already exists: {update_id}")
    if first_date > last_date:
        raise DerivedMarketStoreError("invalid update effective-date window")
    if updates and first_date <= updates[-1].last_effective_date:
        raise DerivedMarketStoreError(
            "normal derived-market updates are append-only and may not overlap the published "
            f"high-water mark {updates[-1].last_effective_date}; use an explicit correction/rebuild path"
        )


def _query_columns(
    query: DerivedMarketQuery,
    feature_set: DerivedFeatureSetDefinition,
) -> tuple[str, ...]:
    allowed = set(feature_set.feature_columns)
    requested = query.feature_columns or feature_set.feature_columns
    unknown = sorted(set(requested).difference(allowed))
    if unknown:
        raise DerivedMarketStoreError(
            f"query references feature columns outside {feature_set.key}: {tuple(unknown)}"
        )
    return ("security_id", "effective_date", "eligible", *tuple(requested))


def _stream_key(universe_id: str, feature_set_key: str) -> str:
    return f"{universe_id}|{feature_set_key}"


def _safe_path_component(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    readable = "".join(character if character.isalnum() or character in {"-", "_"} else "_" for character in value)
    return f"{readable[:80]}__{digest}"
