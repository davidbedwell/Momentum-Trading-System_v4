"""Canonical GA6-v3-with-defense daily permission tape.
Today's open uses yesterday's close-confirmed A-v2/B/B1/C/R1 state.
"""
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state

def permissions(dates, raw_risk_veto):
    tape=build_revised_daily_state().sort_values('date').reset_index(drop=True)
    ds=tape.date.dt.strftime('%Y-%m-%d').tolist()
    states=tape.defensive.tolist()
    prior={ds[i]:bool(states[i-1]) for i in range(1,len(ds))}
    wanted=set(dates)
    absent=wanted-set(prior)
    if absent:raise ValueError('Missing prior-session defense evidence: '+repr(sorted(absent)[:5]))
    absent_raw=wanted-set(raw_risk_veto)
    if absent_raw:raise ValueError('Missing raw risk-veto evidence: '+repr(sorted(absent_raw)[:5]))
    return {d:bool(raw_risk_veto[d] is True and not prior[d]) for d in wanted}
