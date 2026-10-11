"""Frozen retrospective GA4 Normal crash mask for 13-window DEV80 study."""
import json,pathlib
import numpy as np
from Core.layered_ga.ga4_oracle_crash_mask import admissible_decisions
ROOT=pathlib.Path(__file__).resolve().parents[1]
EPISODES=ROOT/'Research/Protocols/MTS_REENTRY_THREE_HYPOTHESIS_TEST_FREEZE_20261004.json'
HORIZONS=tuple(range(2,66))
def mask(decision_dates,trading_calendar,episodes_path=EPISODES):
    episodes=json.loads(pathlib.Path(episodes_path).read_text())['episodes']
    allowed=admissible_decisions(decision_dates,trading_calendar,episodes,HORIZONS,offset=10)
    if allowed.shape!=(len(decision_dates),64) or not np.any(allowed):
        raise RuntimeError('13-window crash exclusion coverage invalid')
    return allowed
