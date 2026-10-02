#!/usr/bin/env python3
import argparse,json,heapq,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT,prevol,atr_ratio
SEED=20261002;BOOT=2000;MINN=100
FLOORS=(.50,.75);CAPS=(1.25,1.50,2.00)

def histstat(h):
 a=np.asarray([x[0] for x in h],float);mae=np.asarray([x[1] for x in h],float);wins=a>0
 return {'n':len(a),'ev':float(a.mean()),'win_rate':float(wins.mean()),'avg_win':float(a[wins].mean()) if wins.any() else 0.0,'p10_loss':max(1e-12,-float(np.quantile(a,.10))),'cvar10_loss':max(1e-12,-float(a[a<=np.quantile(a,.10)].mean())),'mae_p10':max(1e-12,-float(np.quantile(mae,.10))),'vol':max(1e-12,float(a.std(ddof=1)))}
def causal(rows):
 by=defaultdict(list)
 for i,r in enumerate(rows):by[r['signal_date']].append(i)
 gh=defaultdict(list);fh=defaultdict(list);glob=[];pending=[];feat={k:np.full(len(rows),np.nan) for k in ['ev','win_rate','avg_win','p10_loss','cvar10_loss','mae_p10','vol','n']};src=np.empty(len(rows),object)
 for d in sorted(by):
  while pending and pending[0][0]<d:
   _,i=heapq.heappop(pending);r=rows[i];x=(float(r['ret']),float(r['mae']));gh[r['genome']].append(x);fh[r['family']].append(x);glob.append(x)
  cache={}
  for i in by[d]:
   r=rows[i]
   if len(gh[r['genome']])>=MINN:key=('genome',r['genome']);h=gh[r['genome']]
   elif len(fh[r['family']])>=MINN:key=('family',r['family']);h=fh[r['family']]
   elif len(glob)>=MINN:key=('global','global');h=glob
   else:key=('unavailable','x');h=None
   src[i]=key[0]
   if h is not None:
    if key not in cache:cache[key]=histstat(h)
    q=cache[key]
    for k in feat:feat[k][i]=q[k]
  for i in by[d]:heapq.heappush(pending,(rows[i]['path'][-1]['date'],i))
 return feat,Counter(src)
def calibrate(score,floor,cap):
 a=np.asarray(score,float);m=np.isfinite(a);raw=np.zeros(len(a));raw[m]=np.maximum(a[m],0);pos=raw[m&(raw>0)];base=float(np.median(pos)) if len(pos) else 1.;lo,hi=0.,1000/max(base,1e-12)
 for _ in range(80):
  mid=(lo+hi)/2;w=np.ones(len(a));w[m]=np.clip(raw[m]*mid,floor,cap)
  if w.mean()>1:hi=mid
  else:lo=mid
 sc=(lo+hi)/2;w=np.ones(len(a));w[m]=np.clip(raw[m]*sc,floor,cap);return w,sc
def groups(rows,d,key):
 s=defaultdict(float)
 for r,x in zip(rows,d):s[r[key]]+=float(x)
 pos=[v for v in s.values() if v>0];tot=sum(pos)
 return {'groups':len(s),'positive':len(pos),'fraction':len(pos)/len(s) if s else 0,'max_positive_share':max(pos)/tot if pos and tot>0 else None}
def boot(rows,d):
 tick=sorted(set(r['ticker'] for r in rows));ix={t:i for i,t in enumerate(tick)};s=np.zeros(len(tick));n=np.zeros(len(tick),int)
 for r,x in zip(rows,d):j=ix[r['ticker']];s[j]+=x;n[j]+=1
 rng=np.random.default_rng(SEED);v=np.empty(BOOT)
 for b in range(BOOT):q=rng.integers(0,len(tick),len(tick));v[b]=s[q].sum()/n[q].sum()
 return [float(np.quantile(v,.025)),float(np.quantile(v,.975))]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();z,m=load(a.cache,a.manifest);rows=[r for r in z['rows'] if r['signal_date']<SPLIT];ret=np.array([r['ret'] for r in rows]);f,src=causal(rows)
 atr=np.array([atr_ratio(r) for r in rows]);rv=np.array([prevol(r) for r in rows]);
 scores={'ev_p10':np.maximum(f['ev'],0)/f['p10_loss'],'ev_cvar10':np.maximum(f['ev'],0)/f['cvar10_loss'],'ev_vol':np.maximum(f['ev'],0)/f['vol'],'winrate_payoff_p10':f['win_rate']*np.maximum(f['avg_win'],0)/f['p10_loss'],'ev_mae':np.maximum(f['ev'],0)/f['mae_p10'],'ev_p10_x_winrate':np.maximum(f['ev'],0)*f['win_rate']/f['p10_loss'],'ev_p10_x_sqrtN':np.maximum(f['ev'],0)*np.sqrt(np.minimum(f['n'],1000)/1000)/f['p10_loss']}
 # causal pre-entry state interactions, broad monotonic modifiers only
 medatr=np.nanmedian(atr);medrv=np.nanmedian(rv)
 scores['ev_p10_low_atr']=scores['ev_p10']*np.where(np.isfinite(atr),np.where(atr<=medatr,1.15,.85),1)
 scores['ev_p10_low_rv']=scores['ev_p10']*np.where(np.isfinite(rv),np.where(rv<=medrv,1.15,.85),1)
 specs=[('equal',np.ones(len(rows)),None,None,None)]
 for nm,s in scores.items():
  for fl in FLOORS:
   for cp in CAPS:
    w,sc=calibrate(s,fl,cp);specs.append((f'{nm}_f{fl}_c{cp}',w,nm,fl,cp))
 W=np.column_stack([x[1] for x in specs]);dates,en,ex,up,lens,ass=build_events(rows);wa,ga,ca=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False);base=metrics(dates,wa[:,0],ga[:,0],ca[:,0]);out=[]
 for j,(nm,w,kind,fl,cp) in enumerate(specs[1:],1):
  d=ret*(w-1);gs={k:groups(rows,d,k) for k in ['ticker','year','family','genome']};ci=boot(rows,d);pm=metrics(dates,wa[:,j],ga[:,j],ca[:,j]);gate={'mean_positive':float(d.mean())>0,'ticker60':gs['ticker']['fraction']>=.60,'year60':gs['year']['fraction']>=.60,'family60':gs['family']['fraction']>=.60,'ticker_conc15':(gs['ticker']['max_positive_share'] or 1)<=.15,'genome_conc15':(gs['genome']['max_positive_share'] or 1)<=.15,'cluster_ci_positive':ci[0]>0,'wealth_gt_equal':pm['terminal_wealth']>base['terminal_wealth'],'not_both_tail_worse':not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05'])};out.append({'name':nm,'score':kind,'floor':fl,'cap':cp,'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'portfolio':pm,'gate':gate,'pre_neighborhood_pass':all(gate.values())})
 # neighborhood stability: same score family must have >=3 passing configs incl candidate
 for c in out:
  c['passing_neighbors']=sum(x['pre_neighborhood_pass'] for x in out if x['score']==c['score']);c['nominee']=c['pre_neighborhood_pass'] and c['passing_neighbors']>=3
 res={'stage':'GENERAL_WINNER_RULE_DISCOVERY_DEVELOPMENT','protocol_sha256':sha(a.protocol),'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},'score_sources':dict(src),'baseline':base,'candidate_count':len(out),'nominee_count':sum(c['nominee'] for c in out),'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
 Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print('CANDIDATES',len(out),'NOMINEES',res['nominee_count']);
 for c in sorted(out,key=lambda x:x['mean_delta'],reverse=True)[:15]:print(c['name'],'d',round(c['mean_delta'],8),'T',round(c['groups']['ticker']['fraction'],3),'Y',round(c['groups']['year']['fraction'],3),'F',round(c['groups']['family']['fraction'],3),'CI',c['ticker_cluster_ci95'],'pre',c['pre_neighborhood_pass'],'nom',c['nominee'])
 print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()
