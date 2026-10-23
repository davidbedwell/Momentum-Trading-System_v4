"""GA6-v3 normal/defensive permission from prior-session A-v2/B/B1/C/R1 only.
The obsolete historical date-list risk veto is deliberately excluded.
"""
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state

def permissions(dates):
    tape=build_revised_daily_state().sort_values('date').reset_index(drop=True)
    ds=tape.date.dt.strftime('%Y-%m-%d').tolist()
    states=tape.defensive.tolist()
    prior={ds[i]:bool(states[i-1]) for i in range(1,len(ds))}
    wanted=set(dates)
    absent=wanted-set(prior)
    if absent:raise ValueError('Missing prior-session defense evidence: '+repr(sorted(absent)[:5]))
    return {d:not prior[d] for d in wanted}
