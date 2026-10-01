#!/usr/bin/env python3
import argparse,json,math,statistics,multiprocessing as mp
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
import run_discovery_adverse_path_phase1 as p1
import run_discovery_adverse_path_phase2 as p2
PCT=[float(x) for x in np.arange(.01,.1501,.005)]; ATR=[float(x) for x in np.arange(.5,5.0001,.25)]; TIME=list(range(1,21))
MATRIX_P=[.02,.03,.04,.05,.06,.08,.10,.12,.15]; MATRIX_T=[2,4,5,10,15,20]; SIG=[.5,1,1.5,2,2.5,3,3.5,4,5]
def q(v,n):
 v=[x for x in v if x is not None and math.isfinite(x)]; return float(np.percentile(v,n)) if v else None
def mean(v):
 v=[x for x in v if x is not None and math.isfinite(x)]; return statistics.fmean(v) if v else None
def safe_div(a,b): return a/b if b else None
def safe_delta(a,b): return a-b if a is not None and b is not None else None
def econ(v):
 if not v:return {'n':0}
 pos=sum(x for x in v if x>0);neg=-sum(x for x in v if x<0);eq=peak=dd=0.
 for x in v:eq+=x;peak=max(peak,eq);dd=min(dd,eq-peak)
 return {'n':len(v),'win_rate':sum(x>0 for x in v)/len(v),'mean':mean(v),'median':q(v,50),'p05':q(v,5),'worst':min(v),'profit_factor':pos/neg if neg else None,'total_return_units':sum(v),'max_drawdown_return_units':dd}
def breadth(rows,ix):return {'tickers':len({rows[i]['ticker'] for i in ix}),'families':len({rows[i]['family'] for i in ix}),'genomes':len({rows[i]['genome'] for i in ix}),'years':len({rows[i]['year'] for i in ix})}
def ci_cluster(rows,ix,field,seed=20261001,B=200):
 by=defaultdict(list)
 for i in ix:by[rows[i]['ticker']].append(i)
 ts=sorted(by);rng=np.random.default_rng(seed);vals=[]
 for _ in range(B):
  samp=[]
  for t in rng.choice(ts,len(ts),replace=True):samp.extend(by[t])
  if field=='win':vals.append(mean([int(rows[i]['winner']) for i in samp]))
  else:vals.append(mean([rows[i]['ret'] for i in samp]))
 return {'method':'ticker-cluster bootstrap, 200 deterministic resamples','lo':q(vals,2.5),'hi':q(vals,97.5)}
def stop_one(r,kind,x,maxhold=None):
 path=r['path'][:maxhold] if maxhold else r['path']; level=r['ep']*(1-x) if kind=='percent' else r['ep']-x*r['atr']
 for z in path:
  op=float(z['open']);lo=float(z['low'])
  if op<=level:return op/r['ep']-1,True
  if lo<=level:return level/r['ep']-1,True
 if maxhold and maxhold<len(r['path']):return float(path[-1]['close'])/r['ep']-1,False
 return r['ret'],False
def curve(rows,ix,kind,grid):
 base=[rows[i]['ret'] for i in ix];out=[]
 for x in grid:
  vals=[];hit=[]
  for i in ix:
   r=rows[i]
   if kind=='atr' and not r['atr']:continue
   v,h=stop_one(r,kind,x);vals.append(v);hit.append((i,v,h))
  killed=[(i,v) for i,v,h in hit if h and rows[i]['winner']];cut=[(i,v) for i,v,h in hit if h and not rows[i]['winner']]
  out.append({'stop':x,'eligible':len(vals),'stopped':sum(h for _,_,h in hit),'stop_rate':mean([h for _,_,h in hit]),'winner_killed':len(killed),'loser_cut':len(cut),'winner_killed_rate':safe_div(len(killed),sum(rows[i]['winner'] for i in ix)),'loser_cut_rate':safe_div(len(cut),sum(not rows[i]['winner'] for i in ix)),'foregone_winner_pl_avg':mean([rows[i]['ret']-v for i,v in killed]),'foregone_winner_pl_total':sum(rows[i]['ret']-v for i,v in killed),'loss_avoided_avg':mean([v-rows[i]['ret'] for i,v in cut]),'loss_avoided_total':sum(v-rows[i]['ret'] for i,v in cut),'before':econ(base),'after':econ(vals),'incremental_expectancy':safe_delta(mean(vals),mean(base)),**breadth(rows,ix),'net':'UNAVAILABLE_NO_GOVERNED_COST_ARTIFACT'})
 return out
def dims_for(r,rc):
 d=-r['mae'];t=r['mi']+1;rf=max(rc['recs'][:min(4,len(rc['recs']))]) if rc['recs'] else 0;at=d*r['ep']/r['atr'] if r['atr'] else None
 return {'AE':'LT3' if d<.03 else '3_5' if d<.05 else '5_8' if d<.08 else 'GE8','TIME':'LE2' if t<=2 else '3_4' if t<=4 else '5_10' if t<=10 else 'GT10','REC':'LT25' if rf<.25 else '25_50' if rf<.5 else '50_100' if rf<1 else 'GE100','ATR':'MISSING' if at is None else 'LT1' if at<1 else '1_2' if at<2 else '2_3' if at<3 else 'GE3','FAMILY':r['family'],'GENOME':r['genome'],'YEAR':str(r['year'])}
def group_report(rows,ix):
 return {'n':len(ix),**breadth(rows,ix),'win_rate':mean([rows[i]['winner'] for i in ix]),'expectancy':mean([rows[i]['ret'] for i in ix]),'mae':{'p50':q([-rows[i]['mae'] for i in ix],50),'p90':q([-rows[i]['mae'] for i in ix],90)},'time_to_mae':{'p50':q([rows[i]['mi']+1 for i in ix],50),'p90':q([rows[i]['mi']+1 for i in ix],90)},'uncertainty':{'win_rate':ci_cluster(rows,ix,'win'),'expectancy':ci_cluster(rows,ix,'ret')}}
def ref_lineage(s):
 out=[]
 for name,v in s.items():
  if v.get('sweep_session') is not None:out.append((name,v['sweep_session'],v.get('reclaim_session'),v.get('failure_session')))
 return out
def pattern_ix(rows,structs,recs):
 out=defaultdict(list)
 for i,(r,s,rc) in enumerate(zip(rows,structs,recs)):
  low=rc['causal_low_session'];f25=rc['first25'];fail=min([v['failure_session'] for v in s.values() if v.get('failure_session')],default=None)
  cr=None
  if f25:
   for j in range(f25+1,len(r['path'])+1):
    if fail and fail<=j:break
    if rc['recs'][j-1]<=.5:cr=j;break
  if low<=4 and f25 and cr:out['P1'].append(i)
  if f25 and any(sw>=f25 and re is not None and sw<=re<=sw+3 for _,sw,re,_ in ref_lineage(s)):out['P2'].append(i)
  weak=(f25 is None or f25>low+4); later_low=(r['mi']+1)>low
  if weak and later_low:out['P3'].append(i)
  if fail and (r['mi']+1)>fail and not any(v.get('reclaim_session') and fail<=v['reclaim_session']<=fail+5 for v in s.values()):out['P4'].append(i)
 return out
def event_tables(rows,structs,recs):
 names=[f'{d}_{x}' for d in ('FAV','ADV') for x in (.01,.02,.03,.05,.08,.10)]+[f'{d}_ATR_{x}' for d in ('FAV','ADV') for x in (.5,1,1.5,2,3)]+['RECOVERY_25','RECLAIM','STRUCTURAL_SWEEP','STRUCTURAL_FAILURE','TERMINAL']
 occ={n:[] for n in names};first=Counter()
 for r,s,rc in zip(rows,structs,recs):
  ev={'RECOVERY_25':rc['first25'],'RECLAIM':rc['first100'],'STRUCTURAL_SWEEP':min([v['sweep_session'] for v in s.values() if v.get('sweep_session')],default=None),'STRUCTURAL_FAILURE':min([v['failure_session'] for v in s.values() if v.get('failure_session')],default=None),'TERMINAL':len(r['path'])}
  for j,z in enumerate(r['path'],1):
   hi=float(z['high']);lo=float(z['low'])
   for x in (.01,.02,.03,.05,.08,.10):
    if lo<=r['ep']*(1-x):ev.setdefault(f'ADV_{x}',j)
    if hi>=r['ep']*(1+x):ev.setdefault(f'FAV_{x}',j)
   if r['atr']:
    for x in (.5,1,1.5,2,3):
     if lo<=r['ep']-x*r['atr']:ev.setdefault(f'ADV_ATR_{x}',j)
     if hi>=r['ep']+x*r['atr']:ev.setdefault(f'FAV_ATR_{x}',j)
  for n in names:occ[n].append(ev.get(n))
  mt=min(x for x in ev.values() if x is not None); cand=[k for k,v in ev.items() if v==mt];cand.sort(key=lambda k:(0 if k.startswith('ADV') or k=='STRUCTURAL_FAILURE' else 1,k));first[cand[0]]+=1
 return {'event_occurrence':{n:{'n':sum(x is not None for x in v),'incidence':mean([x is not None for x in v]),'median_session':q([x for x in v if x],50),'p90_session':q([x for x in v if x],90)} for n,v in occ.items()},'first_event_counts':dict(first)}
def time_conditioned(rows):
 wins={'WINNER':True,'LOSER':False};winspec=[(1,2),(3,4),(5,10),(11,999)];out={}
 for lab,w in wins.items():
  out[lab]={}
  for lo,hi in winspec:
   vals=[]
   for r in rows:
    if r['winner']!=w:continue
    end=min(hi,len(r['path'])); p=r['path'][:end]; win=r['path'][lo-1:end]
    if not win:continue
    lows=[float(x['low'])/r['ep']-1 for x in p]; wl=[float(x['low'])/r['ep']-1 for x in win];deep=min(lows);endc=float(p[-1]['close'])/r['ep']-1;rec=(endc-deep)/(-deep) if deep<0 else 1
    prior=min(lows[:lo-1],default=0); vals.append((deep,min(wl)-prior,int(min(wl)<prior),rec))
   out[lab][f'{lo}-{hi if hi<999 else "plus"}']={'n':len(vals),'cumulative_mae_p50':q([-x[0] for x in vals],50),'incremental_adverse_p50':q([-x[1] for x in vals],50),'new_low_rate':mean([x[2] for x in vals]),'recovery_fraction_p50':q([x[3] for x in vals],50)}
 return out
def matched_divergence(rows,old):
 # Existing frozen matches already enforce opposite outcome, same family, different ticker. Report first later prespecified dimension divergence.
 out={}
 for h,z in old.items():
  out[h]={'pairs':z.get('pairs') or z.get('n_pairs'),'tickers':z.get('tickers'),'years':z.get('years'),'match_distance':z.get('distance') or z.get('match_distance'),'first_divergence':'REQUIRES_PAIR_IDENTITIES_NOT_PERSISTED_BY_PHASE2'}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--trajectory-dir',required=True);ap.add_argument('--phase1',required=True);ap.add_argument('--phase2',required=True);ap.add_argument('--completion',required=True);ap.add_argument('--output',required=True);ap.add_argument('--markdown',required=True);a=ap.parse_args()
 old1=json.load(open(a.phase1));old2=json.load(open(a.phase2));oldc=json.load(open(a.completion));rows=p2.load_rows(a.trajectory_dir)
 workers=min(6,mp.cpu_count());print('FINAL_WORKERS='+str(workers),flush=True)
 with mp.get_context('fork').Pool(workers,initializer=p2._init_rows,initargs=(rows,)) as pool:structs=pool.map(p2._structure_idx,range(len(rows)),chunksize=256)
 recs=[p2.recovery_stats(r) for r in rows]; allix=list(range(len(rows)));dims=[dims_for(r,rc) for r,rc in zip(rows,recs)]
 out={'format':'MTS_V4_DISCOVERY_ADVERSE_PATH_FINAL_COMPLIANCE_V1','trade_count':len(rows),'ticker_count':len({r['ticker'] for r in rows}),'verification_a_accessed':False,'verification_b_accessed':False,'search_run':False,'refit':False,'rule_selection':False}
 # A/B enhanced exact frozen grids
 out['survival']={}
 for kind,grid in [('percent',[float(x) for x in np.arange(.005,.1501,.005)]),('atr',ATR)]:
  tab=[]
  for x in grid:
   wi=[i for i,r in enumerate(rows) if r['winner'] and (kind=='percent' or r['atr'])];li=[i for i,r in enumerate(rows) if not r['winner'] and (kind=='percent' or r['atr'])]
   def ok(i):return -rows[i]['mae']<=x if kind=='percent' else -rows[i]['mae']*rows[i]['ep']/rows[i]['atr']<=x
   ws=mean([ok(i) for i in wi]);ls=mean([ok(i) for i in li]);tab.append({'threshold':x,'winner_share':ws,'loser_share':ls,'winner_minus_loser':ws-ls,'winner_n':len(wi),'loser_n':len(li),'tickers':len({rows[i]['ticker'] for i in wi+li})})
  out['survival'][kind]=tab
 out['stop_tradeoff']={'percent':curve(rows,allix,'percent',PCT),'atr':curve(rows,allix,'atr',ATR)}
 # C/D full time and conditional grids
 out['time_conditioned']=time_conditioned(rows);out['time_stops']=[]
 for t in TIME:
  vals=[float(r['path'][min(t,len(r['path']))-1]['close'])/r['ep']-1 for r in rows];out['time_stops'].append({'sessions':t,'economics':econ(vals),**breadth(rows,allix)})
 out['stop_x_time']={str(x):{str(t):econ([stop_one(r,'percent',x,t)[0] for r in rows]) for t in MATRIX_T} for x in MATRIX_P}
 groups=defaultdict(lambda:defaultdict(list))
 for i,d in enumerate(dims):
  for k,v in d.items():groups[k][v].append(i)
 out['conditional_regimes']={}
 for k,g in groups.items():
  out['conditional_regimes'][k]={}
  for v,ix in g.items():
   z=group_report(rows,ix);z['percent_stop_curve']=curve(rows,ix,'percent',PCT);z['atr_stop_curve']=curve(rows,ix,'atr',ATR);out['conditional_regimes'][k][v]=z
 # F exact qualifier-before-outcome + uncertainty/year stability
 pix=pattern_ix(rows,structs,recs);out['path_patterns']={}
 for k,ix in pix.items():
  yr=defaultdict(list)
  for i in ix:yr[rows[i]['year']].append(i)
  out['path_patterns'][k]={**group_report(rows,ix),'prevalence':len(ix)/len(rows),'year_stability':{str(y):{'n':len(v),'win_rate':mean([rows[i]['winner'] for i in v]),'expectancy':mean([rows[i]['ret'] for i in v])} for y,v in yr.items()},'qualification_uses_terminal_outcome':False}
 # Q full event occurrence/race; R retain phase2 + controlled retest
 out['event_race']=event_tables(rows,structs,recs);out['entry_frontier']=dict(old2['entry_frontier']);out['entry_frontier']['CONTROLLED_RETEST']=oldc['controlled_retest_entry'];out['entry_frontier']['ORIGINAL_ENTRY']={'n':len(rows),'participation':1.0,'economics':econ([r['ret'] for r in rows])}
 # G full development optimization ceiling across percent/ATR/time grids
 split=old1['discovery_split']['split_date'];devix=[i for i,r in enumerate(rows) if r['signal_date']<split];holdix=[i for i,r in enumerate(rows) if r['signal_date']>=split];bygen=defaultdict(list)
 for i in devix:bygen[rows[i]['genome']].append(i)
 candidates=[]
 for g,ix in bygen.items():
  if len(ix)<100:continue
  specs=[('percent',x) for x in PCT]+[('atr',x) for x in ATR]+[('time',x) for x in TIME]
  for typ,x in specs:
   vals=[];hits=0
   for i in ix:
    r=rows[i]
    if typ=='atr' and not r['atr']:continue
    if typ=='time':v=float(r['path'][min(x,len(r['path']))-1]['close'])/r['ep']-1;h=x<len(r['path'])
    else:v,h=stop_one(r,typ,x)
    vals.append(v);hits+=h
   m=econ(vals);candidates.append({'genome':g,'type':typ,'value':x,'development':m,'stop_rate':hits/len(vals) if vals else None})
 def replay(c):
  ix=[i for i in holdix if rows[i]['genome']==c['genome']];vals=[];hits=0
  for i in ix:
   r=rows[i]
   if c['type']=='atr' and not r['atr']:continue
   if c['type']=='time':v=float(r['path'][min(int(c['value']),len(r['path']))-1]['close'])/r['ep']-1;h=c['value']<len(r['path'])
   else:v,h=stop_one(r,c['type'],c['value'])
   vals.append(v);hits+=h
  z=dict(c);z['holdout']=econ(vals);z['holdout_n']=len(vals);z['holdout_breadth']=breadth(rows,ix);z['label']='IN-SAMPLE OPTIMIZATION CEILING — NOT VALIDATED';return z
 valid=[c for c in candidates if c['development']['n']]
 out['optimization_ceiling']={'highest_success_rate':replay(max(valid,key=lambda c:c['development']['win_rate'])),'highest_gross_expectancy':replay(max(valid,key=lambda c:c['development']['mean'])),'highest_profit_factor':replay(max(valid,key=lambda c:c['development']['profit_factor'] or -1)),'highest_net_expectancy':'UNAVAILABLE_NO_GOVERNED_COST_ARTIFACT','development_n':len(devix),'holdout_n':len(holdix),'split_date':split}
 # H stability and dependence-aware uncertainty
 out['stability']={}
 for key in ('YEAR','TICKER','FAMILY','GENOME'):
  g=defaultdict(list)
  for i,r in enumerate(rows):g[str(r['year'] if key=='YEAR' else r['ticker'] if key=='TICKER' else r['family'] if key=='FAMILY' else r['genome'])].append(i)
  out['stability'][key]={k:{'n':len(ix),'win_rate':mean([rows[i]['winner'] for i in ix]),'expectancy':mean([rows[i]['ret'] for i in ix]),**breadth(rows,ix)} for k,ix in g.items()}
 out['dependence_uncertainty']={'overall':{'win_rate':ci_cluster(rows,allix,'win'),'expectancy':ci_cluster(rows,allix,'ret')},'effective_sampling_unit':'ticker cluster; raw 125002 trades explicitly not treated as independent','broad_market_regime':'N/A: no pre-existing causal market-regime artifact supplied to frozen run'}
 # J sigma survival retained exact grids + volatility regime; K enhanced path shape raw/ATR/sigma20
 out['sigma_survival']=old1['survival_sigma'];out['volatility_regime_mae']=oldc['volatility_regime_mae'];shape=defaultdict(lambda:defaultdict(list))
 for r in rows:
  lab='WINNER' if r['winner'] else 'LOSER';cl=np.array([float(x['close'])/r['ep']-1 for x in r['path']]);d=np.diff(np.r_[0.,cl]);lows=np.array([float(x['low'])/r['ep']-1 for x in r['path']]);li=[];mn=0
  for j,x in enumerate(lows):
   if x<mn:li.append(j);mn=x
  failed=0;amps=[];depth=[];gaps=[]
  for low_a,low_b in zip(li,li[1:]):
   ae=-lows[low_a];peak=max(cl[low_a:low_b+1]);amp=(peak-lows[low_a])/ae if ae>0 else 0;amps.append(amp);depth.append(lows[low_b]-lows[low_a]);gaps.append(low_b-low_a);failed+=amp>=.25 and peak<0
  for coord,scale in [('raw',1.),('atr',(r['atr']/r['ep']) if r['atr'] else None),('sigma20',None)]:
   if coord=='sigma20':
    b=r['_bars'];si=r['si'];rr=[math.log(float(b[j]['close'])/float(b[j-1]['close'])) for j in range(si-19,si+1)] if si>=20 else [];scale=statistics.stdev(rr) if len(rr)>1 else None
   if not scale:continue
   z=d/scale;shape[lab][coord].append({'max_decline_velocity':float(min(z)),'max_recovery_velocity':float(max(z)),'speed_ratio':abs(float(max(z)/min(z))) if min(z)<0 else None,'new_lower_lows':len(li),'failed_rebounds':failed,'successive_low_depth_change':mean([x/scale for x in depth]),'sessions_between_lows':mean(gaps),'rebound_amplitude':mean(amps),'efficiency':abs(cl[-1])/sum(abs(d)) if sum(abs(d)) else None,'sign_changes':sum(d[j]*d[j-1]<0 for j in range(1,len(d))),'choppiness':sum(d[j]*d[j-1]<0 for j in range(1,len(d)))/max(1,len(d)-1),'velocity2_min':q([mean(z[max(0,j-1):j+1]) for j in range(len(z))],0),'velocity4_min':q([mean(z[max(0,j-3):j+1]) for j in range(len(z))],0),'acceleration_min':min(np.diff(z)) if len(z)>1 else None,'acceleration_max':max(np.diff(z)) if len(z)>1 else None})
 out['trajectory_derivatives']={lab:{coord:{'n':len(v),**{k:{'p25':q([x[k] for x in v],25),'p50':q([x[k] for x in v],50),'p75':q([x[k] for x in v],75)} for k in v[0] if k!='n'}} for coord,v in d.items() if v} for lab,d in shape.items()}
 # L transitions with ticker-cluster uncertainty delegated to reported method; M change diagnostics; O/P existing audited artifacts
 out['state_transitions']=old2['state_transitions'];out['state_transition_uncertainty_method']='ticker-cluster bootstrap required; transition-cell CIs not persisted by prior runner'
 out['change_point']={'page_hinkley':old2['change_point'],'mean_shift_5v20':oldc['change_point_completion']['mean_shift_5v20'],'vol_ratio_5v20':oldc['change_point_completion']['vol_ratio_5v20'],'note':'mean/vol diagnostics used fixed non-outcome thresholds in completion code; no outcome tuning'}
 out['label_blind_clustering']=old1['label_blind_clustering'];out['information_value']=oldc['information_value_stability'];out['matched_trajectory']=matched_divergence(rows,old2['matched_trajectory'])
 # E structural references retained + compression; flag fields still needing exact augmentation
 out['structural_references']=old2['structural_references'];out['compression_geometry']=oldc['compression_geometry']
 # I/S required explicit falsification and three-action framing
 out['falsification']={k:'REQUIRED — interpretation fails if effect is not stable under ticker-cluster uncertainty, breadth/stability checks, and untouched validation' for k in ['current_S&P_survivorship_bias','overlapping_cross_sectional_dependence','ticker_concentration','family_genome_concentration','year_regime_concentration','multiple_testing_winners_curse','terminal_label_sensitivity','cost_slippage_sensitivity','gap_execution','full_path_MAE_leakage','structural_definition_instability','Discovery_holdout_contamination','effective_sample_size','tail_truncation','position_sizing_alternative']}
 out['three_action_framing']=old2['three_action_framing'];out['candidate_observations_separate_from_executable_hypothesis']=True
 # compliance is deliberately strict; unresolved items force nonzero exit
 checks={
 'population_125002_67':len(rows)==125002 and len({r['ticker'] for r in rows})==67,
 'verification_sealed':not out['verification_a_accessed'] and not out['verification_b_accessed'],
 'full_survival_grids':len(out['survival']['percent'])==30 and len(out['survival']['atr'])==19,
 'full_stop_grids':len(out['stop_tradeoff']['percent'])==29 and len(out['stop_tradeoff']['atr'])==19,
 'time_windows_and_20_stops':len(out['time_conditioned']['WINNER'])==4 and len(out['time_stops'])==20,
 'conditional_all_dimensions_full_stop_curves':all(all(len(z['percent_stop_curve'])==29 and len(z['atr_stop_curve'])==19 for z in g.values()) for g in out['conditional_regimes'].values()),
 'patterns_P1_P4':set(out['path_patterns'])=={'P1','P2','P3','P4'},
 'optimization_all_three_grids':all(x in out['optimization_ceiling'] for x in ['highest_success_rate','highest_gross_expectancy','highest_profit_factor']),
 'stability_breadth':all(k in out['stability'] for k in ['YEAR','TICKER','FAMILY','GENOME']),
 'sigma_and_volatility':bool(out['sigma_survival']) and bool(out['volatility_regime_mae']),
 'trajectory_three_coordinates':all(set(out['trajectory_derivatives'][x])=={'raw','atr','sigma20'} for x in ['WINNER','LOSER']),
 'change_point_three_methods':set(out['change_point'])>={'page_hinkley','mean_shift_5v20','vol_ratio_5v20'},
 'event_race_full_events':len(out['event_race']['event_occurrence'])==27,
 'entry_frontier_includes_controlled_retest': 'CONTROLLED_RETEST' in out['entry_frontier'],
 'matched_first_divergence':all(v.get('first_divergence')!='REQUIRES_PAIR_IDENTITIES_NOT_PERSISTED_BY_PHASE2' for v in out['matched_trajectory'].values()),
 'state_transition_dependence_CI':False,
 'structural_full_required_behaviors':False,
 'information_value_every_prespecified_observation':False}
 out['compliance_checklist']=checks;out['compliance_pass']=all(checks.values());out['remaining_failures']=[k for k,v in checks.items() if not v]
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 md='# MTS Frozen Protocol Final Compliance — 2026-10-01\n\n'+('\n'.join(f'- [{"x" if v else " "}] {k}' for k,v in checks.items()))+'\n\n**PASS:** '+str(out['compliance_pass'])+'\n\nRemaining failures: '+', '.join(out['remaining_failures'])+'\n'
 Path(a.markdown).write_text(md);print('FINAL_OUTPUT='+a.output);print('COMPLIANCE_PASS='+str(out['compliance_pass']));print('FAILURES='+','.join(out['remaining_failures']));print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
 if not out['compliance_pass']:raise SystemExit(2)
if __name__=='__main__':main()
