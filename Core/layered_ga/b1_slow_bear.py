"""B1: sustained SPY downtrend AND causal funding stress. Independent OR crash input.

Research candidate only: no live deployment or certified PIT data feed.
"""
from dataclasses import dataclass
from collections import deque

@dataclass
class B1SlowBear:
    """Use unadjusted SPY close, trailing 200-close SMA, and precomputed PIT OFR percentile."""
    funding_percentile_floor: float = .70
    below_sma_sessions: int = 10

    def __post_init__(self):
        self.closes = deque(maxlen=200)
        self.below_streak = 0

    def update(self, *, spy_close: float, lagged_funding_percentile: float | None) -> bool:
        if not isinstance(spy_close, (int,float)) or not 0 < spy_close < float('inf'):
            raise ValueError('valid SPY close required')
        self.closes.append(float(spy_close))
        if len(self.closes)<200:
            self.below_streak=0
            return False
        sma=sum(self.closes)/200
        self.below_streak=self.below_streak+1 if spy_close<sma else 0
        if lagged_funding_percentile is None:
            return False
        if not 0 <= lagged_funding_percentile <= 1:
            raise ValueError('PIT funding percentile must be in [0,1]')
        return self.below_streak>=self.below_sma_sessions and lagged_funding_percentile>=self.funding_percentile_floor
