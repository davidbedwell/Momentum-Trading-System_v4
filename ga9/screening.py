"""Daily close-only momentum shortlist and explicitly dated membership evidence."""
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class ScreenPolicy:
    top_k: int = 20
    horizons: tuple = (20, 60, 120)
    def __post_init__(self):
        if self.top_k < 1 or not self.horizons or min(self.horizons) < 1:
            raise ValueError('Positive screen size and horizons required')
    def record(self):
        return asdict(self)


def membership_mask(dates, symbols, path=None):
    """Half-open effective intervals; evidence must be known by interval start.

    No supplied history means fixed research cohort, never survivor-free certification.
    Membership constrains decisions; raw marks remain available for incumbent exits.
    """
    if path is None:
        return np.ones((len(dates), len(symbols)), dtype=bool)
    d = pd.read_csv(path)
    required = {'ticker', 'effective_from', 'effective_to', 'known_at'}
    if not required.issubset(d.columns):
        raise ValueError('Membership requires ticker, effective_from, effective_to, known_at')
    for col in required - {'ticker'}:
        d[col] = pd.to_datetime(d[col], errors='raise')
    if d.effective_from.isna().any() or d.known_at.isna().any() or (d.known_at > d.effective_from).any():
        raise ValueError('Membership evidence must be known by effective_from')
    if ((d.effective_to.notna()) & (d.effective_to <= d.effective_from)).any():
        raise ValueError('Invalid membership interval')
    missing = set(symbols) - set(d.ticker)
    if missing:
        raise ValueError(f'Missing membership history: {sorted(missing)}')
    mask = np.zeros((len(dates), len(symbols)), dtype=bool)
    for j, symbol in enumerate(symbols):
        previous_end = None
        for row in d[d.ticker == symbol].sort_values('effective_from').itertuples():
            if previous_end is not None and (pd.isna(previous_end) or row.effective_from < previous_end):
                raise ValueError('Overlapping membership intervals')
            mask[:, j] |= (dates >= row.effective_from) & (dates < row.effective_to if pd.notna(row.effective_to) else True)
            previous_end = row.effective_to
    return mask


def daily_screen(total_return, close, eligible, policy):
    """Equal-weight percentile ranks of multi-horizon returns and 50-day trend.

    Fixed rules, positive momentum at every horizon; deterministic symbol-order ties.
    Own-price history may precede membership; cross-sectional peers never do.
    """
    components = [total_return / total_return.shift(h) - 1 for h in policy.horizons]
    trend = close / close.rolling(50, min_periods=50).mean() - 1
    parts = components + [trend]
    score = sum(x.where(eligible).rank(axis=1, pct=True) for x in parts) / len(parts)
    valid = eligible & np.logical_and.reduce([x.gt(0).to_numpy() for x in parts])
    score = score.where(valid)
    rank = score.rank(axis=1, ascending=False, method='first')
    return score.to_numpy(), rank.le(policy.top_k).to_numpy()
