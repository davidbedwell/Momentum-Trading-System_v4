from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Mapping, Protocol, Sequence
import time

from .derived_feature_factory import FORWARD_HORIZONS, build_matured_outcome_rows, build_predictor_rows, standard_outcome_feature_set, standard_predictor_feature_set
from .derived_market_store import DerivedMarketStore, DerivedMarketStoreError, UniverseDefinition, acquisition_start_for_plan, plan_incremental_update
from .universe_membership import IntervalMembership


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


def _attach_membership_and_identity(*, membership: IntervalMembership, source: DailyMarketSource, start_date: str, end_date: str, shares_source: PointInTimeSharesSource | None, download_workers: int = 6, download_attempts: int = 4) -> list[dict[str, Any]]:
    if download_workers < 1:
        raise DerivedMarketStoreError("download_workers must be >= 1")
    if download_attempts < 1:
        raise DerivedMarketStoreError("download_attempts must be >= 1")

    def fetch_nonempty(ticker: str) -> Sequence[Mapping[str, Any]]:
        last_error: Exception | None = None
        for attempt in range(1, download_attempts + 1):
            try:
                result = source.fetch(ticker=ticker, start_date=start_date, end_date=end_date)
                if result:
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

def _validate_complete_observed_cross_sections(*, rows: Sequence[Mapping[str, Any]], membership: IntervalMembership, start_date: str, end_date: str) -> Mapping[str, int]:
    """Fail closed when an observed market date is missing an eligible member.

    This catches partial ticker/vendor failures. A future exchange-calendar adapter
    can additionally detect an entirely missing market session; absent that
    authoritative calendar we do not fabricate sessions from weekdays.
    """
    observed: dict[str, set[str]] = {}
    for row in rows:
        effective = str(row.get("date") or row.get("effective_date") or "")[:10]
        if start_date <= effective <= end_date:
            observed.setdefault(effective, set()).add(str(row["security_id"]))
    for effective, securities in sorted(observed.items()):
        expected = {item.security_id for item in membership.members_on(effective)}
        if securities != expected:
            missing = sorted(expected - securities)
            unexpected = sorted(securities - expected)
            raise DerivedMarketStoreError(
                f"incomplete point-in-time cross-section on {effective}: missing={missing[:20]} unexpected={unexpected[:20]} expected_n={len(expected)} observed_n={len(securities)}"
            )
    return {effective: len(securities) for effective, securities in observed.items()}


def maintain_standard_market_store(*, store: DerivedMarketStore, universe: UniverseDefinition, membership: IntervalMembership, source: DailyMarketSource, through_date: str, initial_start_date: str | None = None, shares_source: PointInTimeSharesSource | None = None, update_id_prefix: str = "market-update", publish_outcomes: bool = True, download_workers: int = 6, download_attempts: int = 4) -> DerivedMarketMaintenanceResult:
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
    raw_rows = _attach_membership_and_identity(membership=membership, source=source, start_date=acquisition_start, end_date=through_date, shares_source=shares_source, download_workers=download_workers, download_attempts=download_attempts)
    if not raw_rows:
        raise DerivedMarketStoreError("market source returned no rows for a required incremental update; high-water mark not advanced")
    cross_section_counts = _validate_complete_observed_cross_sections(rows=raw_rows, membership=membership, start_date=first_new, end_date=through_date)

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
                "observed_cross_section_counts": dict(cross_section_counts),
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

    return DerivedMarketMaintenanceResult(
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
