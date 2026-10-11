"""Retrospective GA4 research exclusion. Not a deployable crash detector."""
import numpy as np
import pandas as pd


def frozen_episode_intervals(calendar, episodes, offset=10):
    """Inclusive excluded intervals: peak+offset sessions through trough+offset sessions."""
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar)).normalize().unique().sort_values()
    if len(sessions) < 2 or offset < 0:
        raise ValueError('invalid calendar/offset')
    intervals = []
    for name, dates in episodes.items():
        peak, trough = pd.Timestamp(dates['peak']).normalize(), pd.Timestamp(dates['trough']).normalize()
        if peak not in sessions or trough not in sessions or peak >= trough:
            raise ValueError(f'episode dates absent/out of order: {name}')
        i, j = sessions.get_loc(peak) + offset, sessions.get_loc(trough) + offset
        if j >= len(sessions):
            raise ValueError(f'episode beyond calendar: {name}')
        intervals.append((sessions[i], sessions[j]))
    return intervals


def admissible_decisions(frame_dates, calendar, episodes, horizons, offset=10):
    """Fail closed if any entry-to-exit path touches an excluded session.

    Entries execute at T+1 open; exit is T+1+h open. The returned
    matrix is row x horizon, with no calendar stitching.
    """
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar)).normalize().unique().sort_values()
    intervals = frozen_episode_intervals(sessions, episodes, offset)
    excluded = np.zeros(len(sessions), dtype=bool)
    for start, end in intervals:
        excluded |= (sessions >= start) & (sessions <= end)
    dates = pd.DatetimeIndex(pd.to_datetime(frame_dates)).normalize()
    loc = sessions.get_indexer(dates)
    if (loc < 0).any():
        raise ValueError('decision date missing from trading calendar')
    cumulative = np.r_[0, np.cumsum(excluded.astype(np.int64))]
    result = np.zeros((len(loc), len(horizons)), dtype=bool)
    for j, h in enumerate(horizons):
        if h < 1: raise ValueError('invalid horizon')
        entry, exit_ = loc + 1, loc + 1 + h
        within = exit_ < len(sessions)
        indices = np.flatnonzero(within)
        result[indices, j] = cumulative[exit_[indices] + 1] == cumulative[entry[indices]]
    return result
