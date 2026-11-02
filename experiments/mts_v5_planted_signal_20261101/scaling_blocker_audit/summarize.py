"""Analyze saved replays only: no extra portfolio executions."""
import audit as a
import json,gzip,statistics as st
from collections import Counter,defaultdict
OUT=a.OUT
r=json.loads((OUT/'report.json').read_text())
rows=[];native_counts=Counter();evidence_profiles={};riskprofiles={};dust=[]
with gzip.open(OUT/'original_decision_risk.jsonl.gz','rt') as f:
 for line in f:
  x=json.loads(line);x['risk_audit']=x['risk'];seed,q,v=x['seed'],x['quality'],x['variant']
  days,tapes,_=a.r.s1.generate(seed);tape=tapes['null' if q=='misnull' else q]
  zz=a.extract(x,days,seed,q,v,tape)
  queues=defaultdict(list)
  for dec in x['decisions']:
   if dec.get('reservation_detail'):queues[dec['date']].append(dec)
   if dec.get('context',{}).get('held'):
    ac=next((ac for owner,ac,w in dec.get('actions',[]) if ac in ('ADD','HOLD','EXIT','REDUCE')),None)
    native_counts[q+'_'+v+'_'+str(ac)]+=1
  for dd,ds in queues.items():ds.sort(key=lambda d:(-d.get('allocation_priority',0),d['ticker'],d['selected'][0],d['selected'][1]))
  index={d:i for i,(d,_) in enumerate(days)}
  exits=defaultdict(list)
  for dec in x['decisions']:
   if dec.get('selected') and dec['selected'][2]=='EXIT' and index[dec['date']]+1<len(days):exits[dec['ticker']].append(days[index[dec['date']]+1][0])
  for z in zz:
   d,t=z['date'],z['ticker'];ds=queues.get(d,[])
   z['queue_rank']=next((i+1 for i,dec in enumerate(ds) if dec['ticker']==t),None)
   z['higher_ranked_funded_requests']=[dict(ticker=dec['ticker'],score=dec['allocation_priority'],funded=dec['reservation_detail']['funded']) for dec in ds[:(z['queue_rank'] or 1)-1] if dec['reservation_detail']['funded']>0]
   z['aggregate_risk_alone_exhausted']=z['other_equity_risk']>=.02-1e-12
   z['evidence_cap_15_pass']=bool(z['evidence']) and not a.evidence_fail(z['evidence'],.15)
   z['evidence_cap_20_pass']=bool(z['evidence']) and not a.evidence_fail(z['evidence'],.20)
   # Operative total rejection separates simultaneous target constraints from stage reached.
   z['aggregate_denies_any_increment']=bool(z['reservation']) and z['reservation']['cap_target']>z['current']+1e-12 and z['reservation']['approved']<=z['current']+1e-12 and z['standalone_target_loss']<=.02+1e-12
   detail=z['reservation_detail'];need=max(0,min(z['requested'],.02/z['per_dollar_loss'])-z['current'])*(1+a.r.s1.FRICTION)*(1+a.r.s1.COSTS['fees'])
   initial=detail.get('initial_cash_weight',z['cash']/z['nav']);unsettled=sum(v for _,v in z['unsettled'])/z['nav']
   z['E_settlement_alone_would_cover_shortfall']='E' in z['categories'] and initial+unsettled>=need-1e-12
   z['E_insufficient_even_including_receivables']='E' in z['categories'] and initial+unsettled<need-1e-12
   next_exit=next((dd for dd in exits[t] if dd>d),None)
   z['diagnostic_next_exit']=next_exit
   z['diagnostic_forward_return_to_next_native_exit']=None if next_exit is None else days[index[next_exit]][1][t].open/days[min(index[d]+1,len(days)-1)][1][t].open-1
   z['diagnostic_whole_trade_realized_return']=next((rr['return'] for rr in x['realized'] if rr['ticker']==t and rr['date']==next_exit),None)
  rows.extend(zz)
  dust.append(dict(seed=seed,quality=q,variant=v,realized_records=len(x['realized']),tiny_exit_records=sum(rr['quantity']<.01 for rr in x['realized'])))
with gzip.open(OUT/'unique_opportunities.jsonl.gz','wt') as f:
 for z in rows:f.write(json.dumps(z)+'\n')
r['groups']={}
for q in a.r.QUALITIES:
 for v in ('scale15','scale20'):
  rr=[z for z in rows if z['quality']==q and z['variant']==v];g=a.count(rr)
  g.update(other_risk_alone_at_least_2pct=sum(z['aggregate_risk_alone_exhausted'] for z in rr),aggregate_denies_any_standalone_safe_increment=sum(z['aggregate_denies_any_increment'] for z in rr),settlement_alone_covers_cash_shortfall=sum(z['E_settlement_alone_would_cover_shortfall'] for z in rr),insufficient_cash_even_including_receivables=sum(z['E_insufficient_even_including_receivables'] for z in rr),evidence_15_pass=sum(z['evidence_cap_15_pass'] for z in rr),evidence_20_pass=sum(z['evidence_cap_20_pass'] for z in rr),other_risk_min=min(z['other_equity_risk'] for z in rr),other_risk_median=st.median(z['other_equity_risk'] for z in rr),other_risk_max=max(z['other_equity_risk'] for z in rr))
  r['groups'][q+'_'+v]=g
r['all_variant_observations']=a.count(rows)
dedup={}
for z in rows:
 key=(z['seed'],z['quality'],z['date'],z['ticker'])
 if key not in dedup:dedup[key]=set()
 dedup[key].update(z['categories'])
r['deduplicated_across_targets']=dict(stock_dates=len(dedup),category_union_counts=dict(Counter(k for cats in dedup.values() for k in cats)))
cases=[z for z in rows if z['quality']=='strong' and z['variant']=='scale15' and z['native_action']=='ADD' and not z['evidence_failed_fields'] and z['other_exhausts'] and 'E' not in z['categories'] and 'F' not in z['categories'] and z['current']>=.09 and (z['diagnostic_forward_return_to_next_native_exit'] or 0)>.03]
cases.sort(key=lambda z:z['net_ev'],reverse=True)
chosen=[];seen=set()
for z in cases:
 if z['ticker'] in seen:continue
 seen.add(z['ticker']);chosen.append(z)
 if len(chosen)==8:break
assert len(chosen)>=5
r['cases']=chosen;r['native_incumbent_action_counts']=dict(native_counts);r['evidence_record_dust_diagnostic']=dust
r['root_cause']='2% per-trade limit incorrectly reused as aggregate budget for scaling at manager reservation and kernel evidence gating; ordinary entry gate is per position.'
r['double_counting_finding']='No blanket literal doubling: manager other_equity_risk covers other existing positions; reserved_loss covers queue-funded increments, normally disjoint. It does reserve ordinary increments too. Kernel uses max(other_equity_risk,reserved_risk), not their sum. Both wrongly make other trades consume the per-trade allowance; stale close-time floors survive exits and kernel reservation precedes cash fills.'
r['intended_constraint']='For each admitted increase, total candidate post-trade weight * (max(stop_distance,gap_risk) + round_trip_cost) <= 0.02. Other holdings do not consume that trade budget. Optional aggregate guard must use a distinct explicitly configured limit and de-duplicated portfolio risk state.'
r['tests']=dict(final_passes=6,log='tests.log',initial_fixture_errors='initial_test_fixture_failures.log',original_instrumentation_setup_error='initial_instrumentation_failure.log',regression_portfolio_day_executions_final=13,regression_portfolio_day_executions_initial=12,setup_failed_portfolio_attempts=1)
r['corrected_comparison_scope']='12 seeds 1101-1112, calibrated strong tapes only, 10/15/20%, 36 corrected portfolios; 72 unchanged-policy audit replays for all 3 qualities at 15/20%. Test day executions counted separately; no search.'
r['source_unchanged']=all(a.sha(p)==r['original_sources_sha256'][str(p)] for p in a.SOURCES)
assert r['source_unchanged']
(OUT/'report.json').write_text(json.dumps(r,indent=2))
print(json.dumps(dict(groups=r['groups'],cases=[(z['seed'],z['ticker'],z['date']) for z in chosen],dedup=r['deduplicated_across_targets']),indent=2))
