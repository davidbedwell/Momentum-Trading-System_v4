"""Chronological shadow trade warmup from authentic native GA6 entry signal rows.
Research approximation: fixed 10-session hold, next-open entry/exit, fee .1%
per side. Not native GA6 exits; no broker/portfolio parity certification.
"""
from collections import defaultdict
from causal_calibration import Calibrator,TradeOutcome

def build_shadow_outcomes(signal_rows,bars_by_day,dates,hold=10,fee=.001):
    """signal_rows iterable (signal_date,ticker,chromosome_id).
    bars_by_day maps date -> ticker -> (open,close).
    No outcome is visible before its exit session.
    """
    index={d:i for i,d in enumerate(dates)}
    observations=[]
    seen=set()
    for day,ticker,cid in signal_rows:
        if day not in index:continue
        i=index[day]
        key=(cid,ticker,i)
        if key in seen:continue
        seen.add(key)
        entry=i+1
        exit_i=entry+hold
        if exit_i>=len(dates):continue
        entry_bar=bars_by_day.get(dates[entry],{}).get(ticker)
        exit_bar=bars_by_day.get(dates[exit_i],{}).get(ticker)
        if not entry_bar or not exit_bar:continue
        entry_price=entry_bar[0]
        exit_price=exit_bar[0]
        if entry_price<=0 or exit_price<=0:continue
        net=(exit_price*(1-fee))/(entry_price*(1+fee))-1
        observations.append(TradeOutcome(cid,("GA6_ENTRY",),i,exit_i,net,"shadow"))
    return observations

def seed_calibrator(calibrator,outcomes):
    for outcome in outcomes:calibrator.record(outcome)
    return calibrator
