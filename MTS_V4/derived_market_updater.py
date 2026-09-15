from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, timedelta
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
import time

from .derived_feature_factory import FORWARD_HORIZONS, build_matured_outcome_rows, build_predictor_rows, standard_outcome_feature_set, standard_predictor_feature_set
from .derived_market_store import DerivedMarketStore, DerivedMarketStoreError, UniverseDefinition, acquisition_start_for_plan, plan_incremental_update
from .universe_membership import IntervalMembership, MembershipInterval


class DailyMarketSource(Protocol):
    source_identity: str
    def fetch(self, *, ticker: str, start_date: str, end_date: str) -> Sequence[Mapping[str, Any]]: ...


class PointInTimeSharesSource(Protocol):
    source_identity: str
    def shares_on(self, *, security_id: str, effective_date: str) -> float | None: ...


@dataclass(frozen=True, slots=True)
class DerivedMarketMaintenanceResult:
    universe_id: str
    predictor_update_id: str | None
    predictor_first_date: str | None
    predictor_last_date: str | None
    predictor_rows: int
    outcome_update_id: str | None
    outcome_first_date: str | None
    outcome_last_date: str | None
    outcome_rows: int
    source_rows: int
    acquisition_start: str
    acquisition_end: str


@dataclass(frozen=True, slots=True)
class CrossSectionValidationResult:
    observed_counts: Mapping[str, int]
    tradable_start_adjustments: tuple[Mapping[str, Any], ...]


class TemporaryMarketAcquisitionCache:
    """Restart-safe raw acquisition checkpoints, removed after successful publication."""

    FORMAT = "MTS_V4_TEMPORARY_MARKET_ACQUISITION_CACHE_V1"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _key(*, source_identity: str, ticker: str, start_date: str, end_date: str) -> str:
        payload = f"{source_identity}|{ticker}|{start_date}|{end_date}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _path(self, *, source_identity: str, ticker: str, start_date: str, end_date: str) -> Path:
        return self.root / f"{self._key(source_identity=source_identity, ticker=ticker, start_date=start_date, end_date=end_date)}.json.gz"

    def load(self, *, source_identity: str, ticker: str, start_date: str, end_date: str) -> tuple[Mapping[str, Any], ...] | None:
        path = self._path(source_identity=source_identity, ticker=ticker, start_date=start_date, end_date=end_date)
        if not path.exists():
            return None
        try:
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                document = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return None
        expected = {
            "format": self.FORMAT,
            "source_identity": source_identity,
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
        }
        if any(document.get(key) != value for key, value in expected.items()):
            return None
        rows = document.get("rows")
        if not isinstance(rows, list) or not rows or not all(isinstance(row, Mapping) for row in rows):
            return None
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if document.get("rows_sha256") != hashlib.sha256(canonical.encode("utf-8")).hexdigest():
            return None
        if document.get("row_count") != len(rows):
            return None
        return tuple(dict(row) for row in rows)

    def store(self, *, source_identity: str, ticker: str, start_date: str, end_date: str, rows: Sequence[Mapping[str, Any]]) -> None:
        normalized = [dict(row) for row in rows]
        canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), allow_nan=False)
        document = {
            "format": self.FORMAT,
            "source_identity": source_identity,
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "row_count": len(normalized),
            "first_observed_date": min(str(row.get("date", ""))[:10] for row in normalized),
            "last_observed_date": max(str(row.get("date", ""))[:10] for row in normalized),
            "rows_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "rows": normalized,
        }
        path = self._path(source_identity=source_identity, ticker=ticker, start_date=start_date, end_date=end_date)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with gzip.open(temporary, "wt", encoding="utf-8") as handle:
            json.dump(document, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
        temporary.replace(path)

    def write_audit(self, document: Mapping[str, Any]) -> Path:
        path = self.root / "cross_section_audit.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)
        return path

    def clear_after_success(self) -> None:
        for path in self.root.iterdir():
            if path.is_file() and (path.name.endswith(".json.gz") or path.name == "cross_section_audit.json"):
                path.unlink()
        try:
            self.root.rmdir()
        except OSError:
            pass


def _next_calendar_day(value: str) -> str:
    return (date.fromisoformat(value) + timedelta(days=1)).isoformat()


def _safe_id(value: str) -> str:
    safe = "".join(character if character.isalnum() or character in "-_." else "_" for character in value.strip())
    if not safe:
        raise DerivedMarketStoreError("update_id_prefix must contain at least one safe character")
    return safe


def _ensure_definitions(store: DerivedMarketStore, universe: UniverseDefinition):
    existing_universe = store.get_universe(universe.universe_id)
    if existing_universe is None:
        store.register_universe(universe)
    elif existing_universe != universe:
        raise DerivedMarketStoreError(f"universe definition changed for {universe.universe_id}; create a new version/id rather than mutate history")
    predictor_set = standard_predictor_feature_set()
    outcome_set = standard_outcome_feature_set()
    for feature_set in (predictor_set, outcome_set):
        existing = store.get_feature_set(feature_set.feature_set_id, feature_set.version)
        if existing is None:
            store.register_feature_set(feature_set)
        elif existing != feature_set:
            raise DerivedMarketStoreError(f"feature set changed for {feature_set.feature_set_id}:{feature_set.version}; bump the version")
    return predictor_set, outcome_set


def _attach_membership_and_identity(*, membership: IntervalMembership, source: DailyMarketSource, start_date: str, end_date: str, shares_source: PointInTimeSharesSource | None, download_workers: int = 6, download_attempts: int = 4, acquisition_cache: TemporaryMarketAcquisitionCache | None = None) -> list[dict[str, Any]]:
    if download_workers < 1:
        raise DerivedMarketStoreError("download_workers must be >= 1")
    if download_attempts < 1:
        raise DerivedMarketStoreError("download_attempts must be >= 1")

    def fetch_nonempty(ticker: str) -> Sequence[Mapping[str, Any]]:
        if acquisition_cache is not None:
            cached = acquisition_cache.load(
                source_identity=source.source_identity,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )
            if cached:
                print(f"MARKET_ACQUISITION_CACHE_HIT TICKER={ticker} ROWS={len(cached)}", flush=True)
                return cached
        last_error: Exception | None = None
        for attempt in range(1, download_attempts + 1):
            try:
                result = source.fetch(ticker=ticker, start_date=start_date, end_date=end_date)
                if result:
                    if acquisition_cache is not None:
                        acquisition_cache.store(
                            source_identity=source.source_identity,
                            ticker=ticker,
                            start_date=start_date,
                            end_date=end_date,
                            rows=result,
                        )
                    return result
                last_error = DerivedMarketStoreError(f"market source returned zero rows for {ticker}")
            except Exception as exc:
                last_error = exc
            if attempt < download_attempts:
                delay = min(2 ** (attempt - 1), 8)
                print(
                    f"MARKET_ACQUISITION_RETRY TICKER={ticker} ATTEMPT={attempt + 1}/{download_attempts} DELAY_SECONDS={delay} ERROR={type(last_error).__name__}",
                    flush=True,
                )
                time.sleep(delay)
        raise DerivedMarketStoreError(
            f"market acquisition failed after {download_attempts} attempts for {ticker}: {type(last_error).__name__}: {last_error}"
        ) from last_error
    intervals = membership.active_between(start_date, end_date)
    acquired: dict[int, Sequence[Mapping[str, Any]]] = {}
    with ThreadPoolExecutor(max_workers=download_workers, thread_name_prefix="mts-market-download") as executor:
        futures = {
            executor.submit(
                fetch_nonempty,
                interval.ticker,
            ): (index, interval.ticker)
            for index, interval in enumerate(intervals)
        }
        completed = 0
        try:
            for future in as_completed(futures):
                index, ticker = futures[future]
                acquired[index] = future.result()
                completed += 1
                print(
                    f"MARKET_ACQUISITION_COMPLETED={completed}/{len(intervals)} TICKER={ticker}",
                    flush=True,
                )
        except Exception:
            for pending in futures:
                pending.cancel()
            raise

    # Restore deterministic membership order before identity attachment,
    # validation, feature construction, and publication.
    rows: list[dict[str, Any]] = []
    for index, interval in enumerate(intervals):
        for raw in acquired[index]:
            effective = str(raw.get("date", ""))[:10]
            if not effective or not interval.contains(effective):
                continue
            row = dict(raw)
            row.update({
                "security_id": interval.security_id,
                "ticker": interval.ticker,
                "date": effective,
                "eligible": True,
                "eligibility_reason": "POINT_IN_TIME_UNIVERSE_MEMBER",
                "sector_id": interval.sector_id,
                "industry_id": interval.industry_id,
                "shares_outstanding": shares_source.shares_on(security_id=interval.security_id, effective_date=effective) if shares_source is not None else None,
            })
            rows.append(row)
    identities: set[tuple[str, str]] = set()
    for row in rows:
        identity = (str(row["security_id"]), str(row["date"]))
        if identity in identities:
            raise DerivedMarketStoreError(f"duplicate source security/date during maintenance: {identity}")
        identities.add(identity)
    return rows

def _validate_complete_observed_cross_sections(*, rows: Sequence[Mapping[str, Any]], membership: IntervalMembership, start_date: str, end_date: str, acquisition_cache: TemporaryMarketAcquisitionCache | None = None) -> CrossSectionValidationResult:
    """Fail closed when an observed market date is missing an eligible member.

    This catches partial ticker/vendor failures. A future exchange-calendar adapter
    can additionally detect an entirely missing market session; absent that
    authoritative calendar we do not fabricate sessions from weekdays.
    """
    observed: dict[str, set[str]] = {}
    observed_by_interval: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        effective = str(row.get("date") or row.get("effective_date") or "")[:10]
        if start_date <= effective <= end_date:
            security_id = str(row["security_id"])
            ticker = str(row.get("ticker") or "")
            observed.setdefault(effective, set()).add(security_id)
            observed_by_interval.setdefault((security_id, ticker), set()).add(effective)
    observed_dates = tuple(sorted(observed))
    tradable_starts: dict[MembershipInterval, str] = {}
    adjustments: list[Mapping[str, Any]] = []
    error_examples: list[Mapping[str, Any]] = []
    error_count = 0
    for interval in membership.active_between(start_date, end_date):
        key = (interval.security_id, interval.ticker)
        interval_dates = sorted(
            effective
            for effective in observed_by_interval.get(key, ())
            if interval.contains(effective)
        )
        if not interval_dates:
            error_count += 1
            if len(error_examples) < 200:
                error_examples.append({
                    "type": "NO_ELIGIBLE_HISTORY",
                    "security_id": interval.security_id,
                    "ticker": interval.ticker,
                    "membership_start": interval.start_date,
                    "membership_end": interval.end_date,
                })
            continue
        first_observed = interval_dates[0]
        tradable_starts[interval] = first_observed
        leading_observed_sessions = [
            effective
            for effective in observed_dates
            if max(start_date, interval.start_date) <= effective < first_observed
            and (interval.end_date is None or effective <= interval.end_date)
        ]
        calibration_only = "CALIBRATION_ONLY" in interval.source_identity.upper()
        if len(leading_observed_sessions) > 1 and not calibration_only:
            error_count += 1
            if len(error_examples) < 200:
                error_examples.append({
                    "type": "LEADING_HISTORY_GAP_EXCEEDS_AUTHORIZED_BOUNDARY",
                    "security_id": interval.security_id,
                    "ticker": interval.ticker,
                    "membership_start": interval.start_date,
                    "first_observed": first_observed,
                    "missing_sessions": leading_observed_sessions,
                })
        if leading_observed_sessions:
            reason = (
                "CALIBRATION_CURRENT_TICKER_HISTORY_BEGINS_AFTER_SOURCE_MEMBERSHIP"
                if calibration_only and len(leading_observed_sessions) > 1
                else "SOURCE_MEMBERSHIP_PRECEDES_FIRST_REGULAR_MARKET_OBSERVATION"
            )
            adjustment = {
                "security_id": interval.security_id,
                "ticker": interval.ticker,
                "source_membership_start": interval.start_date,
                "first_regular_market_observation": first_observed,
                "excluded_leading_observed_sessions": tuple(leading_observed_sessions),
                "reason": reason,
            }
            adjustments.append(adjustment)
            print(
                "MARKET_TRADABLE_START_ADJUSTED "
                f"TICKER={interval.ticker} SOURCE_MEMBERSHIP_START={interval.start_date} "
                f"FIRST_REGULAR_OBSERVATION={first_observed} "
                f"EXCLUDED_SESSIONS={','.join(leading_observed_sessions)} REASON={reason}",
                flush=True,
            )
    for effective, securities in sorted(observed.items()):
        expected = {
            item.security_id
            for item in membership.members_on(effective)
            if item in tradable_starts and tradable_starts[item] <= effective
        }
        if securities != expected:
            missing = sorted(expected - securities)
            unexpected = sorted(securities - expected)
            error_count += 1
            if len(error_examples) < 200:
                error_examples.append({
                    "type": "INCOMPLETE_OBSERVED_CROSS_SECTION",
                    "effective_date": effective,
                    "missing": missing[:20],
                    "unexpected": unexpected[:20],
                    "expected_n": len(expected),
                    "observed_n": len(securities),
                })
    result = CrossSectionValidationResult(
        observed_counts={effective: len(securities) for effective, securities in observed.items()},
        tradable_start_adjustments=tuple(adjustments),
    )
    audit = {
        "format": "MTS_V4_CROSS_SECTION_PREFLIGHT_AUDIT_V1",
        "start_date": start_date,
        "end_date": end_date,
        "observed_session_count": len(observed),
        "tradable_start_adjustments": list(adjustments),
        "error_count": error_count,
        "error_examples": error_examples,
        "passed": error_count == 0,
    }
    audit_path = acquisition_cache.write_audit(audit) if acquisition_cache is not None else None
    if error_count:
        location = f" audit={audit_path}" if audit_path is not None else ""
        raise DerivedMarketStoreError(
            f"cross-section preflight found {error_count} defects; examples={error_examples[:20]}{location}"
        )
    return result


def maintain_standard_market_store(*, store: DerivedMarketStore, universe: UniverseDefinition, membership: IntervalMembership, source: DailyMarketSource, through_date: str, initial_start_date: str | None = None, shares_source: PointInTimeSharesSource | None = None, update_id_prefix: str = "market-update", publish_outcomes: bool = True, download_workers: int = 6, download_attempts: int = 4, acquisition_cache_root: str | Path | None = None) -> DerivedMarketMaintenanceResult:
    """Incrementally extend standard predictors and matured outcomes without raw persistence."""
    date.fromisoformat(through_date)
    predictor_set, outcome_set = _ensure_definitions(store, universe)
    safe_prefix = _safe_id(update_id_prefix)
    predictor_state = store.state(universe.universe_id, predictor_set.feature_set_id, predictor_set.version)
    if predictor_state.high_water_mark is None:
        if initial_start_date is None:
            raise DerivedMarketStoreError("initial_start_date is required for an empty predictor stream")
        first_new = initial_start_date
    else:
        first_new = _next_calendar_day(predictor_state.high_water_mark)
    if first_new > through_date:
        return DerivedMarketMaintenanceResult(universe.universe_id, None, None, None, 0, None, None, None, 0, 0, first_new, through_date)

    plan = plan_incremental_update(store=store, universe_id=universe.universe_id, feature_set_id=predictor_set.feature_set_id, feature_set_version=predictor_set.version, first_new_effective_date=first_new, last_new_effective_date=through_date)
    acquisition_start = acquisition_start_for_plan(plan)
    acquisition_cache = TemporaryMarketAcquisitionCache(acquisition_cache_root) if acquisition_cache_root is not None else None
    raw_rows = _attach_membership_and_identity(membership=membership, source=source, start_date=acquisition_start, end_date=through_date, shares_source=shares_source, download_workers=download_workers, download_attempts=download_attempts, acquisition_cache=acquisition_cache)
    if not raw_rows:
        raise DerivedMarketStoreError("market source returned no rows for a required incremental update; high-water mark not advanced")
    cross_section_validation = _validate_complete_observed_cross_sections(rows=raw_rows, membership=membership, start_date=first_new, end_date=through_date, acquisition_cache=acquisition_cache)

    all_predictors = build_predictor_rows(raw_rows)
    predictor_rows = [row for row in all_predictors if first_new <= str(row["effective_date"]) <= through_date]
    predictor_record = None
    if predictor_rows:
        predictor_record = store.append_update(
            universe_id=universe.universe_id,
            feature_set_id=predictor_set.feature_set_id,
            feature_set_version=predictor_set.version,
            update_id=f"{safe_prefix}-predictors-{predictor_rows[0]['effective_date']}-{predictor_rows[-1]['effective_date']}",
            rows=predictor_rows,
            source_lineage={
                "daily_market_source": source.source_identity,
                "membership_sources": sorted({item.source_identity for item in membership.intervals()}),
                "shares_source": shares_source.source_identity if shares_source is not None else None,
                "acquisition_start": acquisition_start,
                "acquisition_end": through_date,
                "observed_cross_section_counts": dict(cross_section_validation.observed_counts),
                "tradable_start_adjustments": list(cross_section_validation.tradable_start_adjustments),
                "partial_cross_sections_allowed": False,
                "raw_rows_persisted": False,
            },
        )

    outcome_record = None
    outcome_rows: list[Mapping[str, Any]] = []
    if publish_outcomes:
        outcome_state = store.state(universe.universe_id, outcome_set.feature_set_id, outcome_set.version)
        all_outcomes = build_matured_outcome_rows(raw_rows)
        mature = [row for row in all_outcomes if row[f"forward_return_{max(FORWARD_HORIZONS)}__v1"] is not None]
        if outcome_state.high_water_mark is not None:
            mature = [row for row in mature if str(row["effective_date"]) > outcome_state.high_water_mark]
        elif initial_start_date is not None:
            mature = [row for row in mature if str(row["effective_date"]) >= initial_start_date]
        outcome_rows = mature
        if outcome_rows:
            outcome_record = store.append_update(
                universe_id=universe.universe_id,
                feature_set_id=outcome_set.feature_set_id,
                feature_set_version=outcome_set.version,
                update_id=f"{safe_prefix}-outcomes-{outcome_rows[0]['effective_date']}-{outcome_rows[-1]['effective_date']}",
                rows=outcome_rows,
                source_lineage={
                    "daily_market_source": source.source_identity,
                    "membership_sources": sorted({item.source_identity for item in membership.intervals()}),
                    "maximum_forward_horizon_sessions": max(FORWARD_HORIZONS),
                    "future_information": True,
                    "raw_rows_persisted": False,
                },
            )

    result = DerivedMarketMaintenanceResult(
        universe_id=universe.universe_id,
        predictor_update_id=predictor_record.update_id if predictor_record else None,
        predictor_first_date=predictor_record.first_effective_date if predictor_record else None,
        predictor_last_date=predictor_record.last_effective_date if predictor_record else None,
        predictor_rows=len(predictor_rows),
        outcome_update_id=outcome_record.update_id if outcome_record else None,
        outcome_first_date=outcome_record.first_effective_date if outcome_record else None,
        outcome_last_date=outcome_record.last_effective_date if outcome_record else None,
        outcome_rows=len(outcome_rows),
        source_rows=len(raw_rows),
        acquisition_start=acquisition_start,
        acquisition_end=through_date,
    )
    if acquisition_cache is not None:
        acquisition_cache.clear_after_success()
    return result


class YFinanceDailyMarketSource:
    """Reacquirable split-adjusted daily OHLCV; never defines historical membership."""
    source_identity = "YFINANCE_DAILY_AUTO_ADJUSTED"

    def fetch(self, *, ticker: str, start_date: str, end_date: str) -> Sequence[Mapping[str, Any]]:
        import yfinance as yf
        exclusive_end = (date.fromisoformat(end_date) + timedelta(days=1)).isoformat()
        frame = yf.download(ticker, start=start_date, end=exclusive_end, auto_adjust=True, actions=False, progress=False, threads=False)
        rows: list[Mapping[str, Any]] = []
        for index, values in frame.iterrows():
            def scalar(name: str) -> float | None:
                value = values[name]
                if hasattr(value, "iloc"):
                    value = value.iloc[0]
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    return None
                return number if number == number else None
            rows.append({"date": index.date().isoformat(), "open": scalar("Open"), "high": scalar("High"), "low": scalar("Low"), "close": scalar("Close"), "volume": scalar("Volume")})
        return rows
