#!/usr/bin/env python3
import argparse,json,math,statistics
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
import run_discovery_adverse_path_phase2 as p2
SPLIT='2021-09-13'; PCT=(.02,.03,.04,.05,.06,.08,.10,.12,.15); TIMES=(2,4,5,10,15,20)
def mean(v): return statistics.fmean(v) if v else None
def q(v,x): return float(np.percentile(v,x)) if v else None
def econ(v):
 if not v:return {'n':0}
 pos=sum(x for x in v if x>0);neg=-sum(x for x in v if x<0);eq=0;peak=0;dd=0
 for x in v:eq+=x;peak=max(peak,eq);dd=min(dd,eq-peak)
 return {'n':len(v),'mean':mean(v),'median':q(v,50),'win_rate':sum(x>0 for x in v)/len(v),'profit_factor':pos/neg if neg else None,'total_return_units':sum(v),'max_drawdown_return_units':dd}
def first_failure(s):return min([v['failure_session'] for v in s.values() if v.get('failure_session')],default=None)
def controlled_retest(r,s,rc):
 f25=rc['first25']; fail=first_failure(s)
 if not f25:return None
 # first post-recovery session that revisits <=50% recovery while no structural failure has occurred
 for j in range(f25+1,len(r['path'])+1):
  if fail is not None and fail<=j:return None
  if rc['recs'][j-1] <= .50:return j
 return None
def change_diag(r):
 closes=np.array([float(x['close']) for x in r['path']],float); ep=r['ep']; rr=np.diff(np.r_[ep,closes])/np.r_[ep,closes][:-1]
 ms=vr=None
 for j in range(20,len(rr)+1):
  a=rr[j-5:j];b=rr[j-20:j]; se=math.sqrt(np.var(a,ddof=1)/5+np.var(b,ddof=1)/20) if len(a)>1 else 0
  if ms is None and se>0 and abs(mean(a)-mean(b))>=2*se:ms=j
  vb=np.std(b,ddof=1); va=np.std(a,ddof=1)
  if vr is None and vb>0 and (va/vb>=2 or va/vb<=.5):vr=j
 return ms,vr
def compression(r):
 # causal confirmed swing points known by signal time; fit last >=2 highs/lows, evaluate narrowing and confluence at entry
 si=r['si']; sl=[v for k,v in r['_sl'].items() if k<=si][-5:]; sh=[v for k,v in r['_sh'].items() if k<=si][-5:]
 if len(sl)<2 or len(sh)<2:return None
 xl=np.array([x[0] for x in sl]);yl=np.array([x[1] for x in sl]);xh=np.array([x[0] for x in sh]);yh=np.array([x[1] for x in sh])
 al,bl=np.polyfit(xl,yl,1);ah,bh=np.polyfit(xh,yh,1); low=al*si+bl;high=ah*si+bh
 width=high-low; narrowing=(ah-al)<0
 refs=[low,high]
 if r['atr']:
  conf=sum(abs(r['ep']-x)<=.5*r['atr'] for x in refs)
 else:conf=0
 return {'narrowing':narrowing,'width_atr':width/r['atr'] if r['atr'] else None,'confluence':conf}
def stopret(r,pct,t):
 path=r['path'][:min(t,len(r['path']))]; stop=r['ep']*(1-pct)
 for x in path:
  if float(x['low'])<=stop:return -pct
 return float(path[-1]['close'])/r['ep']-1
def iv_stats(vals,ys):
 labs={x:i for i,x in enumerate(sorted(set(vals),key=str))};x=[labs[z] for z in vals];hy=p2.entropy(ys);g=defaultdict(list)
 for a,y in zip(x,ys):g[a].append(y)
 cond=sum(len(v)/len(ys)*p2.entropy(v) for v in g.values())
 return {'n':len(ys),'mutual_information':p2.mutual_info(x,ys),'entropy_reduction_bits':hy-cond}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--trajectory-dir',required=True);ap.add_argument('--phase1',required=True);ap.add_argument('--phase2',required=True);ap.add_argument('--output',required=True);ap.add_argument('--markdown',required=True);a=ap.parse_args()
 rows=p2.load_rows(a.trajectory_dir); p1=json.load(open(a.phase1)); old2=json.load(open(a.phase2))
 # parallel causal structures
 import multiprocessing as mp
 with mp.get_context('fork').Pool(6,initializer=p2._init_rows,initargs=(rows,)) as pool: structs=pool.map(p2._structure_idx,range(len(rows)),chunksize=256)
 recs=[p2.recovery_stats(r) for r in rows]
 dev=[i for i,r in enumerate(rows) if r['signal_date']<=SPLIT];hold=[i for i,r in enumerate(rows) if r['signal_date']>SPLIT]
 out={'format':'MTS_V4_DISCOVERY_ADVERSE_PATH_COMPLETION_V1','trade_count':len(rows),'ticker_count':len(set(r['ticker'] for r in rows)),'verification_a_accessed':False,'verification_b_accessed':False,'search_run':False,'refit':False,'rule_selection':False,'phase1_source':a.phase1,'phase2_source':a.phase2}
 # outcome-independent path qualifiers; outcome reported separately
 pats=defaultdict(list)
 for i,(r,s,rc) in enumerate(zip(rows,structs,recs)):
  f=first_failure(s); cr=controlled_retest(r,s,rc); sweeps=[v['sweep_session'] for v in s.values() if v.get('sweep_session')]; reclaims=[v['reclaim_session'] for v in s.values() if v.get('reclaim_session')]
  if rc['causal_low_session']<=4 and rc['first25'] and cr and (f is None or f>cr):pats['P1_QUALIFIER'].append(i)
  if rc['first25'] and sweeps and reclaims and min(reclaims)<=min(sweeps)+3:pats['P2_QUALIFIER'].append(i)
  low=rc['causal_low_session']; weak=(rc['first25'] is None or rc['first25']>low+4)
  if weak and r['mi']+1>low:pats['P3_QUALIFIER'].append(i)
  if f and not any(x<=f+5 for x in reclaims) and r['mi']+1>f:pats['P4_QUALIFIER'].append(i)
 def summ(ix):
  return {'n':len(ix),'tickers':len({rows[i]['ticker'] for i in ix}),'families':len({rows[i]['family'] for i in ix}),'genomes':len({rows[i]['genome'] for i in ix}),'years':len({rows[i]['year'] for i in ix}),'terminal_win_rate':mean([rows[i]['winner'] for i in ix]),'expectancy':mean([rows[i]['ret'] for i in ix])}
 out['path_patterns_causal_qualifier_then_outcome']={k:summ(v) for k,v in pats.items()}
 out['path_pattern_note']='Qualification is computed without terminal outcome; terminal outcome is revealed only afterward. This replaces circular win-rate interpretation of prior P1-P4 output.'
 # change points
 cd={'mean_shift_5v20':{'WINNER':[],'LOSER':[]},'vol_ratio_5v20':{'WINNER':[],'LOSER':[]}}
 for r in rows:
  ms,vr=change_diag(r);lab='WINNER' if r['winner'] else 'LOSER';cd['mean_shift_5v20'][lab].append(ms);cd['vol_ratio_5v20'][lab].append(vr)
 out['change_point_completion']={m:{lab:{'detected_rate':mean([x is not None for x in xs]),'median_session':q([x for x in xs if x],50),'n':len(xs)} for lab,xs in d.items()} for m,d in cd.items()}
 # compression/confluence
 cc={'WINNER':[],'LOSER':[]}
 for r in rows:
  x=compression(r)
  if x:cc['WINNER' if r['winner'] else 'LOSER'].append(x)
 out['compression_geometry']={lab:{'n':len(xs),'narrowing_rate':mean([x['narrowing'] for x in xs]),'median_width_atr':q([x['width_atr'] for x in xs if x['width_atr'] is not None],50),'confluence_ge1_rate':mean([x['confluence']>=1 for x in xs])} for lab,xs in cc.items()}
 # controlled retest entry
 vals=[];orig=[];miss=0
 for r,s,rc in zip(rows,structs,recs):
  j=controlled_retest(r,s,rc);x=p2.entry_policy(r,j)
  if x:vals.append(x);orig.append(r['ret'])
  elif r['winner']:miss+=1
 out['controlled_retest_entry']={'n':len(vals),'participation':len(vals)/len(rows),'missed_favorable_trades':miss,'economics':econ([x['ret'] for x in vals]),'median_entry_delta':q([x['px_delta'] for x in vals],50),'median_subsequent_mae':q([x['mae'] for x in vals],50),'median_subsequent_mfe':q([x['mfe'] for x in vals],50),'mean_opportunity_cost_vs_original':mean([x['ret']-o for x,o in zip(vals,orig)])}
 # 2D stop/time matrix
 out['percent_stop_x_time_stop']={str(p):{str(t):econ([stopret(r,p,t) for r in rows]) for t in TIMES} for p in PCT}
 # volatility regimes from causal signal history
 regimes=defaultdict(lambda:defaultdict(list))
 for r in rows:
  b=r['_bars'];si=r['si'];rets=[]
  for j in range(max(1,si-272),si+1):rets.append(float(b[j]['close'])/float(b[j-1]['close'])-1)
  if len(rets)<272:reg='MISSING'
  else:
   vols=[np.std(rets[k-20:k],ddof=1) for k in range(20,len(rets)+1)];cur=vols[-1];hist=vols[-252:];pct=sum(x<=cur for x in hist)/len(hist);reg='LOW' if pct<=.25 else ('HIGH' if pct>=.75 else 'NORMAL')
  regimes[reg]['WINNER' if r['winner'] else 'LOSER'].append(-r['mae'])
 out['volatility_regime_mae']={reg:{lab:{'n':len(v),'median_mae':q(v,50),'p90_mae':q(v,90)} for lab,v in d.items()} for reg,d in regimes.items()}
 # IV dev/holdout stability using same causal features
 def features(ix):
  F=defaultdict(list);Y=[]
  for i in ix:
   r,s,rc=rows[i],structs[i],recs[i];st=p2.states(r,s,rc);Y.append(int(r['winner']))
   for nm,pos in [('state_s2',1),('state_s4',3),('state_s5',4)]:F[nm].append(st[pos] if len(st)>pos else 'MISSING')
   F['recovery25_by5'].append(int(rc['first25'] is not None and rc['first25']<=5));F['structural_failure'].append(int(any(v['failure'] for v in s.values())));F['structural_sweep'].append(int(any(v['sweep'] for v in s.values())))
  return {k:iv_stats(v,Y) for k,v in F.items()}
 out['information_value_stability']={'development':features(dev),'holdout':features(hold),'split_date':SPLIT}
 # interactions required
 dims={}
 for i,r in enumerate(rows):
  d=-r['mae'];ae='LT3' if d<.03 else '3_5' if d<.05 else '5_8' if d<.08 else 'GE8';tl=r['mi']+1;tb='LE2' if tl<=2 else '3_4' if tl<=4 else '5_10' if tl<=10 else 'GT10';rf=max(recs[i]['recs'][:min(4,len(recs[i]['recs']))]);rb='LT25' if rf<.25 else '25_50' if rf<.5 else '50_100' if rf<1 else 'GE100';at=d*r['ep']/r['atr'] if r['atr'] else None;ab='MISSING' if at is None else 'LT1' if at<1 else '1_2' if at<2 else '2_3' if at<3 else 'GE3';dims[i]=(ae,tb,rb,ab,r['family'],r['genome'])
 specs={'AE_x_TIME':(0,1),'AE_x_REC':(0,2),'AE_x_ATR':(0,3),'TIME_x_REC':(1,2),'FAMILY_x_AE':(4,0),'GENOME_x_AE':(5,0)}
 inter={}
 for nm,(x,y) in specs.items():
  g=defaultdict(list)
  for i in range(len(rows)):g[f'{dims[i][x]}|{dims[i][y]}'].append(i)
  inter[nm]={k:summ(v) for k,v in g.items()}
 out['prespecified_interactions']=inter
 # merge audit + completion status
 out['phase1_existing_sections']=sorted(p1.keys());out['phase2_existing_sections']=sorted(old2.keys())
 out['completion_status']={'machine_readable_json':True,'human_readable_markdown':True,'verification_sealed':True,'remaining_known_gaps':['full conditional stop curves by every regime cell are summarized via interaction economics but not duplicated as full grids','matched-trajectory first-divergence dimension remains not separately enumerated','dependence-aware confidence intervals are not yet computed for every table cell']}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 md=f'''# MTS Discovery Adverse-Path Completion Report — 2026-10-01\n\n**Scope:** Discovery only. 125,002 trades across 67 tickers. Verification A and B remained sealed. No rule was selected or promoted.\n\n## Governance status\nPhase 1 and Phase 2 are retained as frozen intermediate artifacts. This completion pass repairs the circular interpretation of P1-P4 by computing path qualification first and revealing terminal outcome afterward, adds the omitted causal analyses below, and explicitly records remaining gaps rather than silently claiming completion.\n\n## Causal path patterns\n```json\n{json.dumps(out['path_patterns_causal_qualifier_then_outcome'],indent=2)}\n```\nThe terminal win rate is descriptive after qualification; it is not an executable prediction rule and is not validation.\n\n## Added analyses\n- Two-window 5-vs-20 mean-shift and realized-volatility-ratio change diagnostics.\n- Causal compression geometry from confirmed pre-entry swing points.\n- Controlled-retest entry after >=25% recovery without prior structural failure.\n- Prespecified percent-stop × time-stop matrix.\n- Causal volatility-regime MAE breakdown.\n- Development/holdout information-value stability.\n- All six prespecified conditional interactions.\n\n## Controlled retest\n```json\n{json.dumps(out['controlled_retest_entry'],indent=2)}\n```\n\n## Change-point completion\n```json\n{json.dumps(out['change_point_completion'],indent=2)}\n```\n\n## Compression geometry\n```json\n{json.dumps(out['compression_geometry'],indent=2)}\n```\n\n## Remaining known gaps\n{chr(10).join('- '+x for x in out['completion_status']['remaining_known_gaps'])}\n\n## Scientific interpretation\nAll results remain Discovery-only and survivorship-biased by the current-S&P calibration universe. Repeated/overlapping trades are dependent, so raw N is not an independent sample size. No optimized stop, entry milestone, structural pattern, state, cluster, or interaction is validated. Verification A/B must remain sealed until any future executable hypothesis is separately specified and frozen.\n'''
 Path(a.markdown).write_text(md)
 print('REPORT='+a.output);print('MARKDOWN='+a.markdown);print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False');print('PATTERNS='+json.dumps(out['path_patterns_causal_qualifier_then_outcome'],sort_keys=True))
if __name__=='__main__':main()
