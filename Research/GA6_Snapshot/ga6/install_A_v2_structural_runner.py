from pathlib import Path
p=Path('/opt/mts/ga6/structural_independent_v2_20261022/structural_runner_diagnostic.py')
s=p.read_text()
needle=" policy={'membership':{(d,t):v for d,t,v in policy_json['membership'] if d in prepared.dates},'risk_veto':{d:v for d,v in policy_json['risk_veto'].items() if d in prepared.dates},'blocked':{t:frozenset(v) for t,v in policy_json['blocked'].items()},'annual_cash_yield':policy_json['cash_proxy_annual_yield']}"
assert s.count(needle)==1
s=s.replace(needle,needle+'''
 # GA6 A-v2 defense overlay: defensive declaration after close D affects next session open D+1.
 from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
 from ga5_redesign.canonical_engine import digest_file as _hash
 state=build_revised_daily_state().set_index('date')
 state.index=state.index.dt.strftime('%Y-%m-%d')
 trading_dates=sorted(prepared.dates)
 missing=set(trading_dates)-set(state.index)
 if missing:raise ValueError('Crash defense missing dates: '+str(sorted(missing)[:5]))
 defensive=state.defensive.to_dict()
 previous=None
 for day in trading_dates:
  # First session uses the preceding completed market session, not its own close.
  idx=state.index.get_loc(day)
  if idx==0:raise ValueError('No prior crash-defense state for '+day)
  prev=state.iloc[idx-1]
  # Combine with existing policy, never turn an existing veto into permission.
  policy['risk_veto'][day]=bool(policy['risk_veto'][day] is True and not prev.defensive)
 crash_hash=_hash(root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv')
''')
s=s.replace("digest_file(policypath),code,a.population,a.start,a.end", "digest_file(policypath),crash_hash,code,a.population,a.start,a.end")
s=s.replace("batch=StructuralBatch(out,digest_file(source)+a.start+a.end,digest_file(policypath),code)","batch=StructuralBatch(out,digest_file(source)+a.start+a.end,digest_file(policypath)+crash_hash,code)")
# digest_file must refer to refreshed output. Update on each launch.
s=s.replace("state=build_revised_daily_state().set_index('date')","updated=build_revised_daily_state()\n updated.to_csv(root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv',index=False)\n state=updated.set_index('date')")
t=Path('/opt/mts/ga6/structural_independent_v2_20261022/structural_runner_A_v2.py');t.write_text(s)
print('Created',t)
