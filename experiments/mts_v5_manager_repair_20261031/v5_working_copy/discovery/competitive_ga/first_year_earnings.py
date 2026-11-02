"""Native versioned earnings embargo with causal schedule/absence coverage.

Never infer 'no earnings' from an empty event table without dated coverage.
Scheduled future report dates are allowed only when already published as of close.
"""
import pandas as pd
from .first_year_parity import load_native
from .first_year_manifest import day, digest

SOURCES = {
    'ga5_immutable_1_session': '/opt/mts/ga5_earnings_entry_embargo.py',
    'ga6_future_study_2_sessions': '/opt/mts/ga6/earnings_embargo_2_sessions_20261024.py',
}


def native_earnings_clear(*, events, coverage, sessions, tickers, decision_date,
                          decision_at, contract, source_hash):
    if contract not in SOURCES or digest(SOURCES[contract]) != source_hash:
        raise ValueError('unknown or changed native earnings contract')
    sessions = tuple(day(d) for d in sessions)
    if sessions != tuple(sorted(set(sessions))) or decision_date not in sessions:
        raise ValueError('invalid embargo exchange calendar')
    cutoff = pd.Timestamp(decision_at)
    if pd.isna(cutoff) or cutoff.tzinfo is None or str(cutoff.date()) != day(decision_date):
        raise ValueError('explicit dated close required')
    if not {'ticker','event_date','available_at','source_hash'} <= set(events):
        raise ValueError('missing causal earnings schedule schema')
    if not {'ticker','schedule_through','available_at','source_hash'} <= set(coverage):
        raise ValueError('missing verified earnings absence coverage')
    if coverage.ticker.duplicated().any() or set(coverage.ticker) != set(tickers):
        raise ValueError('earnings coverage must match intended universe')
    if set(events.ticker) - set(tickers):
        raise ValueError('foreign earnings ticker')
    for row in coverage.to_dict('records'):
        available = pd.Timestamp(row['available_at'])
        if pd.isna(available) or available.tzinfo is None or available > cutoff or not isinstance(row['source_hash'],str) or not row['source_hash']:
            raise ValueError('uncertified earnings coverage availability')
        # Full declared schedule includes future sessions that can embargo today.
        if day(row['schedule_through']) < sessions[-1]:
            raise ValueError('incomplete forward scheduled-event coverage')
    known = []
    for row in events.to_dict('records'):
        available = pd.Timestamp(row['available_at'])
        if pd.isna(available) or available.tzinfo is None or not isinstance(row['source_hash'],str) or not row['source_hash']:
            raise ValueError('uncertified earnings event availability')
        event_day = day(row['event_date'])
        if available <= cutoff:
            known.append((row['ticker'], event_day))
    native = load_native(SOURCES[contract], 'mts_selected_earnings_embargo')
    result = {}
    for ticker in tickers:
        blocked = native.embargo_sessions([d for t,d in known if t == ticker], sessions)
        result[ticker] = pd.Timestamp(decision_date).date() not in blocked
    return result
